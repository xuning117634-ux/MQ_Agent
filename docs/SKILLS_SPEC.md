# Skills 架构规范（基于 Anthropic 官方标准）

## 1. 什么是 Skill

Skill 是一个自包含的文件夹（"指令包"），教会 Agent 如何处理特定任务或工作流。
Skill 不是代码模块，而是声明式的指令 + 可执行脚本的组合。任何兼容的 Agent 拿到这个文件夹即可使用。

## 2. 目录结构

```
skill-name/                # kebab-case 命名，必须
├── SKILL.md               # 必须，大小写敏感，技能契约文件
├── scripts/               # 可选，可执行代码（Python/Bash）
│   ├── action_a.py
│   └── action_b.py
├── references/            # 可选，补充文档，按需加载
│   └── api-guide.md
├── examples/              # 可选，输入输出示例
│   └── action_a.md
└── assets/                # 可选，模板、图标等静态资源
```

### 命名规则
- 文件夹名：kebab-case（如 `liveevent`、`mqs-service`）
- SKILL.md：必须精确为 `SKILL.md`，不接受 `skill.md`、`SKILL.MD` 等变体
- 不要在技能文件夹内放 README.md

## 3. SKILL.md 格式

### 3.1 YAML Frontmatter（必须）

```yaml
---
name: 技能名称（64字符以内）
description: 技能描述，Agent 用此判断何时触发（200字符以内）
dependencies: httpx>=0.24.0, pyyaml>=6.0
---
```

必填字段：
- `name`：人类可读的技能名称
- `description`：清晰描述技能做什么、何时使用（Agent 靠这个决定是否调用）

可选字段：
- `dependencies`：技能依赖的软件包

### 3.2 Markdown Body

Markdown 正文是技能的完整指令，包含：
- 概述：技能的用途和场景
- Tools 声明：每个可调用工具的定义
- Constraints：约束和限制条件

### 3.3 Tools 声明格式

```markdown
## Tools

### tool_name
工具的描述文字。

**Script:** scripts/tool_name.py

**Parameters:**
- param_name (type, required): 参数描述
- param_name (type, optional): 参数描述
```

支持的 type：`string`、`integer`、`number`、`boolean`

## 4. 三级渐进式披露（Progressive Disclosure）

| 级别 | 内容 | 加载时机 |
|------|------|----------|
| Level 1 | YAML frontmatter | 始终加载到 Agent 系统提示词 |
| Level 2 | SKILL.md Markdown body | 技能被触发时加载 |
| Level 3 | references/、scripts/ | 按需加载执行 |

此设计最小化 token 消耗，同时保持专业能力。

## 5. Scripts 规范

### 5.1 执行协议
- 输入：通过 `stdin` 接收 JSON 格式参数
- 输出：通过 `stdout` 输出 JSON 格式结果
- 退出码：0 = 成功，非 0 = 失败
- 鉴权：通过环境变量读取（如 HW_ID、HW_APPKEY）

### 5.2 独立性要求
- 脚本必须完全独立，不 import 父项目的任何代码
- 仅依赖标准库 + SKILL.md 中声明的 dependencies
- 可直接命令行测试：`echo '{"key":"value"}' | python scripts/action.py`

### 5.3 示例

```python
#!/usr/bin/env python3
"""独立可执行脚本模板"""
import sys
import json
import os

def main():
    input_data = json.loads(sys.stdin.read())
    # ... 业务逻辑 ...
    result = {"success": True, "data": "..."}
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

## 6. Registry 引擎职责

通用 Agent 的 registry 引擎负责：
1. 启动时扫描所有含 SKILL.md 的子文件夹
2. 解析 YAML frontmatter → 生成 OpenAI Tool Calling 格式的 schema
3. 解析 Tools 段 → 提取工具名、描述、参数、脚本路径
4. 工具被调用时 → subprocess 执行对应脚本，stdin 传参，stdout 收结果
5. 提供 `get_skills_context()` → 返回所有 SKILL.md body 供系统提示词注入

## 7. 跨项目复用

将技能文件夹整体拷贝到任何支持此规范的 Agent 的 skills 目录下：
1. 确保目标环境安装了 dependencies 中声明的包
2. 配置所需的环境变量
3. Agent 的 registry 自动发现并注册

## 8. 参考来源
- Anthropic 官方：[How to create custom Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)
- Anthropic 官方：[The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- Anthropic 官方：[Extend Claude with skills](https://code.claude.com/docs/en/skills)