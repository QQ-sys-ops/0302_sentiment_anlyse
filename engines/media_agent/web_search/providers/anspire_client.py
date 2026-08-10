import datetime
from typing import Any

from engines.common.retries import with_retry
from engines.contracts.settings import get_settings
from engines.media_agent.web_search.base import BaseSearchClient
from engines.media_agent.web_search.search_results import (
    SearchProviderResponse,
    WebpageResult,
)

AUTHORITATIVE_SOURCES = (
    "www.gov.cn,news.cn,xinhuanet.com,people.com.cn,"
    "news.cctv.com,chinanews.com.cn"
)
SOCIAL_SOURCES = "weibo.com,zhihu.com,toutiao.com"


class AnspireSearchClient(BaseSearchClient):
    """Anspire Web 检索 Provider 实现。"""

    def __init__(self) -> None:
        """读取 Anspire 密钥与地址并构建请求头。"""
        super().__init__()
        self.api_key = get_settings().ANSPIRE_API_KEY
        self.base_url = get_settings().ANSPIRE_BASE_URL
        self.headers = self.build_request_headers(self.api_key)

    async def comprehensive_search(self, query: str) -> SearchProviderResponse:
        """全量检索,不限站点"""
        return await self._execute_search(query=query, top_k=15)

    async def source_search(self, query: str) -> SearchProviderResponse:
        """在政府与中央媒体站点执行溯源检索。"""
        return await self._execute_search(
            query=query, top_k=10, insite=AUTHORITATIVE_SOURCES
        )

    async def realtime_search(self, query: str) -> SearchProviderResponse:
        """在近一周社交站点范围内执行时效性检索。"""
        to_time = datetime.datetime.now()
        from_time = to_time - datetime.timedelta(weeks=1)
        return await self._execute_search(
            query=query,
            top_k=5,
            insite=SOCIAL_SOURCES,
            from_time=from_time.strftime("%Y-%m-%d %H:%M:%S"),
            to_time=to_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    @with_retry
    async def _execute_search(
            self,
            query: str,
            top_k: int,
            insite: str = "",
            from_time: str = "",
            to_time: str = "",
    ) -> SearchProviderResponse:
        """组装参数发起 GET 并解析响应。"""
        params = {
            "query": query,
            "top_k": top_k,
            "Insite": insite,
            "FromTime": from_time,
            "ToTime": to_time,
        }
        response = await self.send_request(
            "GET",
            self.base_url,
            {"headers": self.headers, "params": params},
        )
        return self._process_response(response, query)

    @staticmethod
    def _process_response(response_dict: dict[str, Any], query: str) -> SearchProviderResponse:
        """将 Anspire 原始结果映射为网页模型。"""
        results = response_dict.get("results", [])
        webpages: list[WebpageResult] = []
        for result in results:
            webpages.append(
                WebpageResult(
                    title=result.get("title"),
                    url=result.get("url"),
                    content=result.get("content"),
                    date=result.get("date"),
                    score=result.get("score"),
                )
            )
        return SearchProviderResponse(
            query=query,
            webpages=webpages,
        )




import asyncio


async def main() -> None:
    client = AnspireSearchClient()

    query = "高考难不难"

    # 1) 全量检索
    res = await client.comprehensive_search(query)
    print(f"[comprehensive_search]: {res.query}, 共获取 {len(res.webpages)} 条结果：\n")
    for item in res.webpages:
        print(f"标题: {item.title}")
        print(f"链接: {item.url}")
        print(f"日期: {item.date}")
        print(f"分数: {item.score}")
        print(f"摘要: {item.content[:100]}...\n")

    # 2) 权威/溯源检索（政府与中央媒体站点）
    res = await client.source_search(query)
    print(f"\n[source_search]: {res.query}, 共获取 {len(res.webpages)} 条结果：\n")
    for item in res.webpages:
        print(f"标题: {item.title}")
        print(f"链接: {item.url}")
        print(f"日期: {item.date}")
        print(f"分数: {item.score}")
        print(f"摘要: {item.content[:100]}...\n")

    # 3) 近一周社交站点时效检索
    res = await client.realtime_search(query)
    print(f"\n[realtime_search]: {res.query}, 共获取 {len(res.webpages)} 条结果：\n")
    for item in res.webpages:
        print(f"标题: {item.title}")
        print(f"链接: {item.url}")
        print(f"日期: {item.date}")
        print(f"分数: {item.score}")
        print(f"摘要: {item.content[:100]}...\n")


if __name__ == "__main__":
    asyncio.run(main())
