import dataclasses
from typing import Any
from loguru import logger
from engines.common.research_graph_runtime import ResearchNode
from engines.contracts.agent_roles import ROLE_INFOS
from engines.insight_agent.state import InsightState
from engines.insight_agent.tools.retrieval_service import InsightRetrievalService


class EvidenceRetrievalNode(ResearchNode):
    """调用私域召回服务获取尚未合并的原始证据。"""

    async def __call__(self, state: InsightState) -> dict[str, Any]:
        """执行私域召回并返回尚未合并的原始命中记录。"""
        role = state['role']
        role_info=ROLE_INFOS[role]

        logger.info(f"{role_info.agent_name} 开始执行私域信息检索")
        evidence_records = await InsightRetrievalService().retrieve_evidence(state["query"])
        logger.info(f"{role_info.agent_name} 私域信息检索完成")
        return {"retrieved_records": evidence_records}



@dataclasses.dataclass
class User:
    name: str


    @property
    def id(self):

        return  "123"



if __name__ == '__main__':

    user= User(name="tome")

    print(user.name)
    print(user.id)


