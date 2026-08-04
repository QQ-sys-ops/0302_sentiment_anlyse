import asyncio
from builtins import ValueError
from typing import TypeVar, Any

from engines.common.retries import with_retry
from pydantic import Field

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel
from engines.contracts.role_rules import ROLE_INFOS, RoleKey
from engines.contracts.settings import get_settings

T = TypeVar("T", bound=BaseModel)  # BaseModel类型


class LLMClient:
    """
    LLM客户端
    """

    def __init__(self,
                 model_name: str,
                 model_provider_name: str,
                 api_key: str,
                 base_url: str
                 ):
        self.model_name = model_name
        self.model_provider_name = model_provider_name
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_role(cls, role: RoleKey) -> "LLMClient":
        """
        根据Agent的角色获取到LLMClient
        :param role:
        :return:
        """
        # 1. 获取角色对象
        role_info = ROLE_INFOS[role]

        # 2. 获取角色的配置信息
        config_prefix = role_info.confix_prefix

        # 3. 获取settings对象
        settings = get_settings()

        # 4. 实例化不同角色的llm客户端
        return cls(
            model_name=getattr(settings, f"{config_prefix}_MODEL_NAME"),
            model_provider_name=getattr(settings, f"{config_prefix}_MODEL_PROVIDER"),
            api_key=getattr(settings, f"{config_prefix}_API_KEY"),
            base_url=getattr(settings, f"{config_prefix}_BASE_URL")

        )

    async def generate_text(self,
                            system_prompt: str,
                            user_prompt: str) -> str:
        """
        返回LLM的文本消息内容
        :param system_prompt:
        :param user_prompt:
        :return:
        """

        # 1. 实例化llm_client

        llm_client = self._build_chat_model(is_structured=False)

        # 2. 调用ainvoke()--------如果llm输出的内容超过2min,怎么解决？方案替换用流式替换非流式

        final_chunks = []
        async for chunk in llm_client.astream(self._build_input(system_prompt, user_prompt)):
            if text := chunk.text:
                final_chunks.append(text)
        # 3. 返回
        return "".join(final_chunks)

    @with_retry
    async def generate_object(self,
                              system_prompt: str,
                              user_prompt: str,
                              object_model: type[T]
                              ) -> T:
        """
        返回Pydantic处理后的结构化对象
        :param system_prompt:
        :param user_prompt:
        :param object_model:
        :return:
        """

        # 1. 实例化llm_client
        llm_client = self._build_chat_model(is_structured=True)

        # 2. 调用xxx  method:json_mode(最弱)  json_schema(最强)  function_calling(支持性最好的):你是怎么理解function_calling?  tool_call:  tool_calls
        structured_output = llm_client.with_structured_output(object_model,
                                                              method="json_schema")  # 100%输出结构化对象   面试：如何保证llm输出结构化对象？
        llm_result = await structured_output.ainvoke(self._build_input(system_prompt, user_prompt))
        if llm_result is None:
            raise ValueError(f"{self.model_name}模型调用失败，返回None")
        # 3. 返回
        return llm_result

    def _build_chat_model(self, is_structured: bool):

        model_name = self.model_name.lower()
        kwargs: dict[str, Any] = {}
        if is_structured and ("kimi" in model_name or "moonshot" in model_name):
            # 禁用思考模式
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
        """

        :param system_prompt:
        :param user_prompt:
        :return:
        """

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]


class Project(BaseModel):
    tech_tracks: list[str] = Field(description="使用的技术栈")


class User(BaseModel):
    name: str = Field(description="用户的名字")
    age: int = Field(description="用户的年龄")
    projects: list[Project] = Field(description="用户参与的项目",default_factory=list)


async def main_test():
    llm_client = LLMClient.from_role(role="insight")
    # result = await llm_client.generate_text(system_prompt="你是一个讲笑话的专家", user_prompt="请您给我讲一个笑话")
    #
    # print(result)
    result = await llm_client.generate_object(
        system_prompt="你是一个用户信息提取方面的专家",
        user_prompt="请从我以下的输入信息中，提取用户的信息："
                    "我的名字叫Tom,今年18岁，我参与过电商项目以及AI多智能体项目的开发，"
                    "电商项目使用的技术栈：SpringBoot、 Redis、MySQL"
                    "AI多智能体项目使用的技术栈: LangChain、LangGraph、LangFuse、LangSmith ",
        object_model=User
    )

    print(result)

if __name__ == '__main__':
    asyncio.run(main_test())
