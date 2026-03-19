"""
Skills Registry Engine
自动扫描技能文件夹、解析 SKILL.md、生成 OpenAI tool schema、subprocess 执行脚本。
遵循 Anthropic Skills 架构规范（详见 docs/SKILLS_SPEC.md）。
"""
import os
import re
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# 全局注册表：{tool_name: {description, script_path, parameters, skill_name, skill_dir}}
_tools_registry = {}
# 技能上下文：{skill_name: {metadata, body}}
_skills_context = {}


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 SKILL.md 的 YAML frontmatter 和 Markdown body"""
    if not content.startswith('---'):
        return {}, content

    end_idx = content.index('---', 3)
    yaml_str = content[3:end_idx].strip()
    body = content[end_idx + 3:].strip()

    metadata = {}
    for line in yaml_str.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('#'):
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    return metadata, body


def _parse_tools_section(body: str) -> list[dict]:
    """从 Markdown body 中解析 ## Tools 段落，提取工具定义"""
    tools = []

    # 找到 ## Tools 段
    tools_match = re.search(r'^## Tools\s*$', body, re.MULTILINE)
    if not tools_match:
        return tools

    tools_text = body[tools_match.end():]
    # 截断到下一个 ## 段落
    next_section = re.search(r'^## ', tools_text, re.MULTILINE)
    if next_section:
        tools_text = tools_text[:next_section.start()]

    # 按 ### 分割每个工具
    tool_blocks = re.split(r'^### ', tools_text, flags=re.MULTILINE)

    for block in tool_blocks:
        block = block.strip()
        if not block:
            continue

        # 第一行是工具名
        lines = block.split('\n')
        tool_name = lines[0].strip()

        # 提取描述（工具名之后、第一个 **xxx:** 之前的文本）
        desc_lines = []
        i = 1
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('**'):
                break
            if line:
                desc_lines.append(line)
            i += 1
        description = ' '.join(desc_lines)

        # 提取 Script 路径
        script_match = re.search(r'\*\*Script:\*\*\s*(.+)', block)
        script_path = script_match.group(1).strip() if script_match else ''

        # 提取 Parameters
        parameters = []
        params_match = re.search(r'\*\*Parameters:\*\*', block)
        if params_match:
            params_text = block[params_match.end():]
            param_pattern = r'^- (\w+)\s*\((\w+),\s*(required|optional)\):\s*(.+)$'
            for m in re.finditer(param_pattern, params_text, re.MULTILINE):
                parameters.append({
                    'name': m.group(1),
                    'type': m.group(2),
                    'required': m.group(3) == 'required',
                    'description': m.group(4).strip()
                })

        tools.append({
            'name': tool_name,
            'description': description,
            'script': script_path,
            'parameters': parameters
        })

    return tools


def scan_skills(skills_dir: str = None):
    """扫描技能目录，注册所有含 SKILL.md 的技能"""
    global _tools_registry, _skills_context

    if skills_dir is None:
        skills_dir = str(Path(__file__).parent)

    skills_path = Path(skills_dir)
    _tools_registry.clear()
    _skills_context.clear()

    for skill_dir in skills_path.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            continue

        try:
            content = skill_md.read_text(encoding='utf-8')
            metadata, body = _parse_frontmatter(content)
            skill_name = metadata.get('name', skill_dir.name)

            # 保存技能上下文
            _skills_context[skill_name] = {
                'metadata': metadata,
                'body': body,
                'dir': str(skill_dir)
            }

            # 解析工具定义
            tools = _parse_tools_section(body)
            for tool in tools:
                script_rel = tool['script']
                script_abs = str(skill_dir / script_rel) if script_rel else ''

                _tools_registry[tool['name']] = {
                    'description': tool['description'],
                    'script_path': script_abs,
                    'parameters': tool['parameters'],
                    'skill_name': skill_name,
                    'skill_dir': str(skill_dir)
                }

            logger.info(f"Registered skill: {skill_name} with {len(tools)} tools")

        except Exception as e:
            logger.error(f"Failed to load skill from {skill_dir}: {e}")


def get_tools_schema() -> list:
    """生成 OpenAI Tool Calling 格式的 schema"""
    tools = []
    for tool_name, info in _tools_registry.items():
        properties = {}
        required = []

        for param in info['parameters']:
            properties[param['name']] = {
                'type': param['type'],
                'description': param['description']
            }
            if param['required']:
                required.append(param['name'])

        tools.append({
            'type': 'function',
            'function': {
                'name': tool_name,
                'description': info['description'],
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required
                }
            }
        })

    return tools


def call_skill(tool_name: str, **kwargs) -> Any:
    """通过 subprocess 执行技能脚本"""
    if tool_name not in _tools_registry:
        raise ValueError(f'Skill tool "{tool_name}" not found')

    info = _tools_registry[tool_name]
    script_path = info['script_path']

    if not script_path or not Path(script_path).exists():
        raise FileNotFoundError(f'Script not found: {script_path}')

    input_json = json.dumps(kwargs, ensure_ascii=False)
    logger.info(f"Executing skill script: {script_path} with input: {input_json}")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=info['skill_dir']
        )

        if result.returncode != 0:
            logger.error(f"Script error (exit {result.returncode}): {result.stderr}")
            return {"error": f"Script failed: {result.stderr.strip()}"}

        return json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        return {"error": "Script execution timed out (30s)"}
    except json.JSONDecodeError:
        return {"error": f"Script returned invalid JSON: {result.stdout[:200]}"}
    except Exception as e:
        return {"error": f"Execution error: {str(e)}"}


def get_skills_context() -> str:
    """返回所有技能的 SKILL.md body，供系统提示词注入"""
    parts = []
    for name, ctx in _skills_context.items():
        parts.append(f"=== Skill: {name} ===\n{ctx['body']}")
    return '\n\n'.join(parts)


def list_skills() -> list:
    """列出所有已注册的工具名"""
    return list(_tools_registry.keys())
