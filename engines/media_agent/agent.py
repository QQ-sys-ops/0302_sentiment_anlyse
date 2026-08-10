import asyncio

from engines.common.llm import LLMClient
from engines.common.reports import get_output_dir
from engines.common.research_graph_runtime import ResearchRunContext, ProgressCallback, handle_research_graph
from engines.contracts.agent_roles import RoleKey
from engines.media_agent.graph import build_graph


async def media_agent_handler(role: RoleKey,
                              query: str,
                              task_id: str,
                              llm_client: LLMClient,
                              output_dir: str,
                              progress_callback: ProgressCallback | None = None
                              ):
    """
    公域找数据
    role:str
    query:str
    task_id:str
    llm_client:LLMClient
    output_dir:str

    :return:
    """
    context = ResearchRunContext(
        task_id=task_id,
        role=role,
        llm_client=llm_client,
        output_dir=output_dir,
        progress_callback=progress_callback,
    )
    await handle_research_graph(context, build_graph(context), query)



async  def  main_test():
    await media_agent_handler(
        role="media",
        query="高考",
        task_id="1234",
        llm_client=LLMClient.from_role("media"),
        output_dir=get_output_dir(task_id="1234",role="media"),
        progress_callback=None
    )


if __name__ == '__main__':

    asyncio.run(main_test())


