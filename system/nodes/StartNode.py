from typing import Any, Dict, Optional

from system.nodes.BaseNode import BaseNode


class StartNode(BaseNode):
    """
    开始节点：
    - 没有输入，只有输出
    - 节点名称默认值为「开始节点」
    """

    DEFAULT_NAME: str = "开始节点"

    def __init__(
        self,
        node_name: Optional[str] = None,
        node_json: Optional[Dict[str, Any]] = None,
    ) -> None:
        # 如果没有传入名称，则使用默认名称
        super().__init__(node_name=node_name or self.DEFAULT_NAME, node_json=node_json)

    # ===== 实例方法：修改当前实例的节点名称和节点 JSON 数据 =====
    def set_node_name(self, name: str) -> None:
        """修改当前实例的节点名称。"""
        self.node_name = name

    def set_node_json(self, data: Dict[str, Any]) -> None:
        """整体替换当前实例的节点 JSON 数据。"""
        self.node_json = data

    # ===== 实例方法：读取节点 JSON 数据 =====
    def get_node_json(self) -> Dict[str, Any]:
        """读取当前实例的节点 JSON 数据。"""
        return self.node_json

    # ===== 实例方法：执行开始节点逻辑 =====
    def run(self, **kwargs) -> Dict[str, Any]:
        # 使用当前实例的 node_json 作为输出
        return self.node_json