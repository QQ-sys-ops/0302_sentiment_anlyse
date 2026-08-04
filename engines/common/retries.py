import asyncio
from functools import wraps

from loguru import logger


class RetryConfig:
    max_retries: int = 3  # 最多重试次数
    init_delay: float = 1.0  # 初始重试时间
    max_delay: float = 60.0
    backoff_factor: float = 2.0  # 回退因子（指数增长）  前面几次重试间隔应该要短一些 后面随着重试次数在增加，间隔长一些

    def _get_delay(self, attempt: int) -> float:
        return min(self.init_delay * 2 ** attempt, self.max_delay)

    def _is_no_retrable(self, exec: Exception) -> bool:
        """
        是否能重试
        :param exec:
        :return:
        429:限流

        """
        stauts_code = getattr(exec, 'status_code', None)
        if stauts_code is None:
            stauts_code = getattr(getattr(exec, 'response', None), 'status_code', None)
        return isinstance(stauts_code, int) and 400 <= stauts_code < 500 and stauts_code != 429

    def get_retry_delay(self,
                        fun_name: str,
                        attempt: int,
                        exec: Exception) -> float | None:

        # 1. 不可以重试
        if self._is_no_retrable or attempt >= self.max_retries:
            return None

        # 2. 计算下一次延时事件
        delay = self._get_delay(attempt)

        current_try = attempt + 1
        next_try = current_try + 1
        logger.warning(f"函数 {fun_name} 第 {current_try} 次尝试失败: {exec}")
        logger.info(f"将在 {delay:.1f} 秒后进行第 {next_try} 次尝试...")
        # 3. 返回延时
        return delay


retry_config = RetryConfig()


async def with_retry(func):
    """
    闭包使用
    :param func:
    :return:
    """
    if not asyncio.iscoroutinefunction(func):
        raise TypeError(
            "重试装饰器只能装饰 async 函数,"
            f"得到的是同步函数 {func.__name__}"
        )
    @wraps(func)
    async def wrapper(*args, **kwargs):
        for attempt in range(retry_config.max_retries+1):
          try:
              return  await  func(*args, **kwargs)
          except Exception as  exec:
              delay=retry_config.get_retry_delay(func.__name__,attempt,exec)
              if delay is None:
                  raise ValueError(f"{func.__name__}不可在重试")
              await asyncio.sleep(delay)

    return wrapper()
