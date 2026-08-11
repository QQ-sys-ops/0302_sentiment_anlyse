"""
任务管理器
1. 管理查询的业务任务---业务方
2. 管理开启的异步任务---底层(异步的协程对象)
"""
import asyncio
import uuid
from dataclasses import dataclass
from typing import Coroutine


@dataclass(slots=True)
class ResearchTask:
    query: str
    task_id: str


class ResearchTaskManager:
    """
    研究任务的任务管理器
    """

    def __init__(self):
        self.research_tasks: dict[str, ResearchTask] = {}
        self.async_tasks: set[asyncio.Task] = set()

    def create_research_task(self, query: str) -> ResearchTask:
        research_task = ResearchTask(query=query, task_id=str(uuid.uuid4().hex))
        self.research_tasks[research_task.task_id] = research_task
        return research_task

    def get_research_task(self, task_id: str) -> ResearchTask:
        return self.research_tasks[task_id]




    def submit_task(self, coroutine: Coroutine) -> asyncio.Task:
        # 1. 将异步任务交给事件循环线程[没有开启新线程，用的还是事件循环的线程]
        task = asyncio.create_task(coroutine)

        # 2. 将异步任务对象存储到容器中
        self.async_tasks.add(task)

        # 3. 等异步任务做完 从容器中移除掉
        task.add_done_callback(self.async_tasks.discard)
        return task

    async def cancel_all_tasks(self) -> None:
        tasks = tuple(task for task in self.async_tasks if not task.done())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)





research_task_manager = ResearchTaskManager()
