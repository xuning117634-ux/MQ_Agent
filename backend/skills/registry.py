import inspect
import json
from typing import Callable, Any

_skills_registry = {}


def register_skill(func: Callable) -> Callable:
    """装饰器：注册一个技能到全局注册表"""
    skill_name = func.__name__
    _skills_registry[skill_name] = func
    return func


def get_tools_schema() -> list:
    """生成 OpenAI Tool Calling 格式的 schema"""
    tools = []
    for skill_name, func in _skills_registry.items():
        sig = inspect.signature(func)
        params = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue

            annotation = param.annotation
            param_type = 'string'
            if annotation == int:
                param_type = 'integer'
            elif annotation == float:
                param_type = 'number'
            elif annotation == bool:
                param_type = 'boolean'

            params[param_name] = {
                'type': param_type,
                'description': f'{param_name} parameter'
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        tool = {
            'type': 'function',
            'function': {
                'name': skill_name,
                'description': func.__doc__ or f'Execute {skill_name} skill',
                'parameters': {
                    'type': 'object',
                    'properties': params,
                    'required': required
                }
            }
        }
        tools.append(tool)

    return tools


def call_skill(skill_name: str, **kwargs) -> Any:
    """调用已注册的技能"""
    if skill_name not in _skills_registry:
        raise ValueError(f'Skill {skill_name} not found')
    return _skills_registry[skill_name](**kwargs)


def list_skills() -> list:
    """列出所有已注册的技能"""
    return list(_skills_registry.keys())
