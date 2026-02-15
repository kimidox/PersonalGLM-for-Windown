from typing import TypedDict, List, Optional

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """定义智能体的状态结构"""
    # 对话历史
    messages: List[BaseMessage]
    # 当前处理的任务
    task: str
    # 任务处理结果（可选）
    result: Optional[str] = None
    # 错误信息（可选）
    error: Optional[str] = None