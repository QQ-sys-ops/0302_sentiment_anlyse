from builtins import ValueError
from typing import TypeVar, Any

from engines.common.retries import with_retry
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel
from engines.contracts.agent_roles import ROLE_INFOS, RoleKey
from engines.contracts.settings import get_settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """LLM客户端"""

    def __init__(self,
                 model_name: str,
                 model_provider_name: str,
                 api_key: str,
                 base_url: str
                 ):
        """初始化大模型客户端的连接配置。"""
        self.model_name = model_name
        self.model_provider_name = model_provider_name
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_role(cls, role: RoleKey) -> "LLMClient":
        """根据Agent的角色获取到LLMClient"""
        role_info = ROLE_INFOS[role]
        config_prefix = role_info.confix_prefix
        settings = get_settings()
        return cls(
            model_name=getattr(settings, f"{config_prefix}_MODEL_NAME"),
            model_provider_name=getattr(settings, f"{config_prefix}_MODEL_PROVIDER"),
            api_key=getattr(settings, f"{config_prefix}_API_KEY"),
            base_url=getattr(settings, f"{config_prefix}_BASE_URL")

        )

    async def generate_text(self,
                            system_prompt: str,
                            user_prompt: str) -> str:
        """返回LLM的文本消息内容"""
        llm_client = self._build_chat_model(is_structured=False)
        final_chunks = []
        async for chunk in llm_client.astream(self._build_input(system_prompt, user_prompt)):
            if text := chunk.text:
                final_chunks.append(text)
        return "".join(final_chunks)

    @with_retry
    async def generate_object(self,
                              system_prompt: str,
                              user_prompt: str,
                              object_model: type[T]
                              ) -> T:
        """返回Pydantic处理后的结构化对象"""

        llm_client = self._build_chat_model(is_structured=True)

        structured_output = llm_client.with_structured_output(object_model, method="json_schema")
        llm_result = await structured_output.ainvoke(self._build_input(system_prompt, user_prompt))
        if llm_result is None:
            raise ValueError(f"{self.model_name}模型调用失败，返回None")
        return llm_result

    def _build_chat_model(self, is_structured: bool):
        """按输出类型构建聊天模型实例。"""

        model_name = self.model_name.lower()
        kwargs: dict[str, Any] = {}
        if is_structured and ("kimi" in model_name or "moonshot" in model_name):
            kwargs['extra_body'] = {
                "thinking": {
                    "type": "disabled"
                }
            }

        return init_chat_model(
            model_provider=self.model_provider_name,
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            **kwargs
        )

    def _build_input(self, system_prompt: str, user_prompt: str) -> list[BaseMessage]:
        """构建消息对象"""

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
