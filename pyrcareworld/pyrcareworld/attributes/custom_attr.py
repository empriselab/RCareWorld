import pyrcareworld.attributes as attr
from pyrcareworld.side_channel.side_channel import (
    IncomingMessage,
    OutgoingMessage,
)
import pyrcareworld.utils.utility as utility


# 消息解析示例
def parse_message(msg: IncomingMessage) -> dict:
    # 先完成所继承的基类的数据读取
    this_object_data = attr.base_attr.parse_message(msg)
    # 按顺序读取数据
    # 此处读取顺序对应Unity的CustomAttr脚本CollectData函数中的写入顺序
    this_object_data["custom_message"] = msg.read_string()
    return this_object_data


# 新增接口示例
def CustomMessage(kwargs: dict) -> OutgoingMessage:
    # 必要参数
    compulsory_params = ["id", "message"]
    # 非必要参数
    optional_params = []
    # 参数检查
    utility.CheckKwargs(kwargs, compulsory_params)

    msg = OutgoingMessage()
    # 第一个写入的数据必须是ID
    msg.write_int32(kwargs["id"])
    # 第二个写入的数据必须是消息类型 此处CustomMessage对应Unity新增Attr脚本AnalysisMsg函数switch的一个分支
    msg.write_string("CustomMessage")
    # 按顺序写入数据
    msg.write_string(kwargs["message"])

    return msg
