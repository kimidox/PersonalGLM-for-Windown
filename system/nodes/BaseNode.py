from typing import Any, Dict, Optional


class BaseNode:
    """
    所有节点类的基类。
    提供两个通用属性：
    - node_name: 节点名称
    - node_json: 节点对应的 JSON 配置数据
    """

    def __init__(
        self,
        node_name: str = "",
        node_json: Optional[Dict[str, Any]] = None,
    ) -> None:
        # 节点名称
        self.node_name: str = node_name
        # 节点 JSON 数据（配置 / 元信息等）
        self.node_json: Dict[str, Any] = node_json or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        将节点信息转换为可序列化的字典，方便持久化或调试。
        """
        return {
            "node_name": self.node_name,
            "node_json": self.node_json,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseNode":
        """
        从字典创建一个节点实例。
        """
        return cls(
            node_name=data.get("node_name", "") or "",
            node_json=data.get("node_json") or {},
        )