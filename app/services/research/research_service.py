from pathlib import Path

from engines.common.reports import get_output_dir
from engines.contracts.agent_roles import RESEARCH_ROLE_KEYS
from engines.orchestrator.orchestrator import OrchestratorAgent
from engines.common.task_manager import research_task_manager


class ResearchService:

    def __init__(self):
        """初始化研究任务编排器"""
        self._orchestrator = OrchestratorAgent()

    def research(self, query: str) -> str:
        """执行研究任务"""
        research_task = research_task_manager.create_research_task(query)
        self._orchestrator.dispatch_task(query, research_task.task_id)
        return research_task.task_id

    def get_research_results(self, task_id: str) -> tuple[str, dict[str, str]]:
        """读取指定研究任务的各角色报告内容"""

        # 1. 获取指定的研究任务，校验任务是否存在
        research_task = research_task_manager.get_research_task(task_id)
        if research_task is None:
            raise LookupError(f"研究任务不存在: {task_id}")

        # 2. 遍历各个研究角色，读取已生成的 Markdown 报告文件内容
        research_results: dict[str, str] = {}
        for role in RESEARCH_ROLE_KEYS:
            report_file = Path(get_output_dir(task_id, role)) / "report.md"
            if not report_file.exists():
                continue
            research_results[role] = report_file.read_text(
                encoding="utf-8", errors="ignore"
            )

        # 3. 返回任务 ID 及包含所有已就绪角色报告的字典
        return research_task.task_id, research_results
