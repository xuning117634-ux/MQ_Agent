import os
import json
import asyncio
import logging
from openai import AsyncOpenAI
from backend.skills.registry import scan_skills, get_tools_schema, call_skill, get_skills_context

logger = logging.getLogger(__name__)


class AgentEngine:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_BASE_URL')
        )
        self.model = os.getenv('LLM_MODEL', 'qwen3.5-plus')
        # 自动扫描并注册所有技能
        scan_skills()
        self.tools = get_tools_schema()
        self.skills_context = get_skills_context()
        logger.info(f"Agent initialized with {len(self.tools)} tools")

    async def chat(self, user_message: str):
        """
        对话引擎，支持 Tool Calling 循环。
        使用 async yield 返回 SSE 事件流，不阻塞事件循环。
        """
        logger.info(f'User message: {user_message}')

        system_prompt = (
            '你是一个消息Agent助手，可以帮助用户管理消息服务。\n'
            '规则：\n'
            '- 对于日常问候、闲聊、问答等普通对话，直接回复即可，不要调用任何工具\n'
            '- 只有当用户明确要求创建、管理消息事件或服务资源时，才调用工具\n'
        )

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_message}
        ]

        # Tool Calling 循环
        while True:
            logger.info(f'Calling LLM with {len(self.tools)} tools')

            # 使用异步流式 API 调用
            api_kwargs = dict(
                model=self.model,
                messages=messages,
                stream=True
            )
            if self.tools:
                api_kwargs['tools'] = self.tools
            stream = await self.client.chat.completions.create(**api_kwargs)

            # 收集完整的 assistant 消息
            full_content = ''
            tool_calls_data = {}  # {index: {id, name, arguments}}

            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                # 流式输出文本
                if delta.content:
                    full_content += delta.content
                    yield f'data: {json.dumps({"type": "text", "content": delta.content})}\n\n'

                # 收集 tool calls（流式返回的 tool call 是分片的）
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_data:
                            tool_calls_data[idx] = {
                                'id': tc.id or '',
                                'name': tc.function.name if tc.function and tc.function.name else '',
                                'arguments': ''
                            }
                        else:
                            if tc.id:
                                tool_calls_data[idx]['id'] = tc.id
                            if tc.function and tc.function.name:
                                tool_calls_data[idx]['name'] = tc.function.name
                        if tc.function and tc.function.arguments:
                            tool_calls_data[idx]['arguments'] += tc.function.arguments

            # 构造 assistant message 添加到历史
            assistant_msg = {'role': 'assistant', 'content': full_content or None}

            if tool_calls_data:
                assistant_msg['tool_calls'] = []
                for idx in sorted(tool_calls_data.keys()):
                    tc = tool_calls_data[idx]
                    assistant_msg['tool_calls'].append({
                        'id': tc['id'],
                        'type': 'function',
                        'function': {
                            'name': tc['name'],
                            'arguments': tc['arguments']
                        }
                    })

            messages.append(assistant_msg)

            # 如果没有 tool calls，对话结束
            if not tool_calls_data:
                logger.info('No tool calls, conversation ended')
                yield f'data: {json.dumps({"type": "done"})}\n\n'
                break

            # 执行 tool calls
            for idx in sorted(tool_calls_data.keys()):
                tc = tool_calls_data[idx]
                tool_name = tc['name']
                try:
                    tool_args = json.loads(tc['arguments'])
                except json.JSONDecodeError:
                    tool_args = {}

                logger.info(f'Executing tool: {tool_name} with args: {tool_args}')
                yield f'data: {json.dumps({"type": "tool_start", "tool_name": tool_name})}\n\n'

                try:
                    result = await asyncio.to_thread(call_skill, tool_name, **tool_args)
                    logger.info(f'Tool result: {result}')
                except Exception as e:
                    logger.error(f'Tool error: {e}')
                    result = {'error': str(e)}

                # 添加 tool 结果到消息历史
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tc['id'],
                    'content': json.dumps(result)
                })

                yield f'data: {json.dumps({"type": "tool_end", "tool_name": tool_name})}\n\n'
