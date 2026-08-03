from typing import Any

from pydantic import RootModel,BaseModel,field_validator,Field


class ConfigUpdateRequest(RootModel[dict[str,Any]]):
    """
     配置更新的请求体数据
    """

    @field_validator("root")
    @classmethod
    def not_empty(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("请求体不能为空")
        return value




class ConfigResponse(BaseModel):
    """
    读取配置信息的响应数据
    """
    config:dict[str,Any]=Field(default_factory=dict,description="读取的最新配置")
