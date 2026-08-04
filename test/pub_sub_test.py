from typing import Any, Callable

# 创建事件总线
container: dict[str, list] = {}


# 创建订阅者
def subscribe(event_type: str, callback: Callable):
    """
    订阅者
    :param event_type:
    :param callback:
    :return:
    """
    if not event_type in container:
        container[event_type] = []

    container[event_type].append(callback)


def tom_to_weather(data: dict[str, Any]):
    print(f"TOM收到了{data}")

def tom1_to_weather(data: dict[str, Any]):
    print(f"TOM1收到了{data}")



def jack_to_tech(data: dict[str, Any]):
    print(f"JACK收到了{data}")


# 创建发布者

def publish(event_type: str, data: dict[str, Any]):
    """
    发布的本质将对应事件类型的数据发送给订阅者 让订阅者消费
    :param event_type:
    :param data:
    :return:
    """

    if event_type in container:
        for callback in container[event_type]:
            callback(data)



# 订阅者先行 核心逻辑在订阅者身上
subscribe("weather",tom_to_weather)
subscribe("weather",tom1_to_weather)
subscribe("tech",jack_to_tech)

publish("weather",data={"city":"深圳","weather":"晴天"})
# publish("tech",data={"AI":"qwen3.8发布了"})






