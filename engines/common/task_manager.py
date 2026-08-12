"""统一任务管理器"""
import asyncio
import uuid
from dataclasses import dataclass
from typing import Coroutine


@dataclass(slots=True)
class ResearchTask:
    query: str
    task_id: str


class ResearchTaskManager:
    """研究任务的任务管理器"""

    def __init__(self):
        """初始化研究任务与异步任务容器"""
        self.research_tasks: dict[str, ResearchTask] = {}
        self.async_tasks: set[asyncio.Task] = set()

    def create_research_task(self, query: str) -> ResearchTask:
        """创建并登记新的研究任务"""
        research_task = ResearchTask(query=query, task_id=str(uuid.uuid4().hex))
        self.research_tasks[research_task.task_id] = research_task
        return research_task

    def get_research_task(self, task_id: str) -> ResearchTask:
        """按任务标识获取研究任务"""
        return self.research_tasks[task_id]

    def submit_task(self, coroutine: Coroutine) -> asyncio.Task:
        """提交协程并跟踪其异步任务"""
        task = asyncio.create_task(coroutine)
        self.async_tasks.add(task)
        task.add_done_callback(self.async_tasks.discard)
        return task

    async def cancel_all_tasks(self):
        """取消并等待所有未完成的异步任务"""
        tasks = tuple(task for task in self.async_tasks if not task.done())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


research_task_manager = ResearchTaskManager()
