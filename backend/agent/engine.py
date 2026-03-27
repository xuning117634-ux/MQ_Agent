import asyncio
import json
import logging
import os

from openai import AsyncOpenAI

from backend.skills.registry import call_skill
from backend.skills.registry import get_skills_context
from backend.skills.registry import get_tools_schema
from backend.skills.registry import scan_skills
os.environ['NO_PROXY'] = '*'
logger = logging.getLogger(__name__)


class AgentEngine:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )
        self.model = os.getenv("LLM_MODEL", "qwen3.5-plus")
        scan_skills()
        self.tools = get_tools_schema()
        self.skills_context = get_skills_context()
        logger.info("Agent initialized with %s tools", len(self.tools))

    def _build_system_prompt(self) -> str:
        return (
            "你是一个消息Agent助手，可以帮助用户管理消息服务。\n"
            "规则：\n"
            "- 对于日常问候、闲聊、问答等普通对话，直接回复即可，不要调用任何工具\n"
            "- 只有当用户明确要求创建、管理消息事件或服务资源时，才调用工具\n"
        )

    def _build_messages(self, user_message: str) -> list[dict]:
        return [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_message},
        ]

    def _build_api_kwargs(self, messages: list[dict]) -> dict:
        api_kwargs = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        if self.tools:
            api_kwargs["tools"] = self.tools
        return api_kwargs

    def _update_tool_call_data(self, tool_calls_data: dict, tool_call) -> None:
        index = tool_call.index
        function = tool_call.function

        tool_call_info = tool_calls_data.setdefault(
            index,
            {"id": "", "name": "", "arguments": ""},
        )

        if tool_call.id:
            tool_call_info["id"] = tool_call.id
        if function and function.name:
            tool_call_info["name"] = function.name
        if function and function.arguments:
            tool_call_info["arguments"] += function.arguments

    async def _read_stream(self, stream):
        full_content = ""
        tool_calls_data = {}

        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue

            if delta.content:
                full_content += delta.content
                yield self._format_sse_event("text", content=delta.content), None, None

            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    self._update_tool_call_data(tool_calls_data, tool_call)

        yield None, full_content, tool_calls_data

    def _build_assistant_message(self, full_content: str, tool_calls_data: dict) -> dict:
        assistant_message = {"role": "assistant", "content": full_content or None}
        if not tool_calls_data:
            return assistant_message

        assistant_message["tool_calls"] = [
            {
                "id": tool_call["id"],
                "type": "function",
                "function": {
                    "name": tool_call["name"],
                    "arguments": tool_call["arguments"],
                },
            }
            for _, tool_call in sorted(tool_calls_data.items())
        ]
        return assistant_message

    def _parse_tool_arguments(self, raw_arguments: str) -> dict:
        try:
            return json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {}

    def _build_tool_message(self, tool_call: dict, result: dict) -> dict:
        return {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(result),
        }

    async def _execute_tool_call(self, tool_call: dict) -> dict:
        tool_name = tool_call["name"]
        tool_args = self._parse_tool_arguments(tool_call["arguments"])
        logger.info("Executing tool: %s with args: %s", tool_name, tool_args)

        try:
            result = await asyncio.to_thread(call_skill, tool_name, **tool_args)
            logger.info("Tool result: %s", result)
            return result
        except Exception as exc:
            logger.error("Tool error: %s", exc)
            return {"error": str(exc)}

    def _format_sse_event(self, event_type: str, **payload) -> str:
        event_payload = {"type": event_type, **payload}
        return f"data: {json.dumps(event_payload)}\n\n"

    async def _run_completion_round(self, messages: list[dict]):
        logger.info("Calling LLM with %s tools", len(self.tools))
        stream = await self.client.chat.completions.create(**self._build_api_kwargs(messages))

        full_content = ""
        tool_calls_data = {}
        async for event, content, tool_calls in self._read_stream(stream):
            if event is not None:
                yield event, None
                continue
            full_content = content
            tool_calls_data = tool_calls

        yield None, (full_content, tool_calls_data)

    async def _handle_tool_calls(self, messages: list[dict], tool_calls_data: dict):
        for _, tool_call in sorted(tool_calls_data.items()):
            tool_name = tool_call["name"]
            yield self._format_sse_event("tool_start", tool_name=tool_name)

            result = await self._execute_tool_call(tool_call)
            messages.append(self._build_tool_message(tool_call, result))

            yield self._format_sse_event("tool_end", tool_name=tool_name)

    async def chat(self, user_message: str):
        logger.info("User message: %s", user_message)
        messages = self._build_messages(user_message)

        while True:
            full_content = ""
            tool_calls_data = {}

            async for event, round_result in self._run_completion_round(messages):
                if event is not None:
                    yield event
                    continue
                full_content, tool_calls_data = round_result

            messages.append(self._build_assistant_message(full_content, tool_calls_data))

            if not tool_calls_data:
                logger.info("No tool calls, conversation ended")
                yield self._format_sse_event("done")
                return

            async for event in self._handle_tool_calls(messages, tool_calls_data):
                yield event
