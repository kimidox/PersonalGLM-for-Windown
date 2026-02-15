import threading
from typing import Dict, Optional

from system.utils import get_config_by_key


class AgentCacheManager:
    def __init__(self, max_size: int = 20):
        self.cache: Dict[str, object] = {}  # 缓存容器：key=标识，value=Agent实例
        self.max_size = int(max_size)  # 最大缓存数量
        self.lock = threading.Lock()  # 线程安全锁（多线程场景必备）
        self.access_count: Dict[str, int] = {}  # 记录实例访问次数，用于LRU淘汰

    def get_agent(self, key: str) -> Optional[object]:
        """
        从缓存获取Agent实例
        :param key: 实例的唯一标识（如 template_id + tenant_id）
        :return: Agent实例或None
        """
        with self.lock:
            if key in self.cache:
                # 更新访问次数（用于LRU淘汰）
                self.access_count[key] += 1
                return self.cache[key]
        return None

    def set_agent(self, key: str, agent: object) -> None:
        """
        将Agent实例存入缓存
        :param key: 实例的唯一标识
        :param agent: Agent实例
        """
        with self.lock:
            # 若缓存已满，淘汰访问次数最少的实例
            if len(self.cache) >= self.max_size:
                least_key = min(self.access_count, key=lambda k: self.access_count[k])
                del self.cache[least_key]
                del self.access_count[least_key]
                print(f"【缓存淘汰】移除 Agent 实例（key：{least_key}）")

            # 存入缓存
            self.cache[key] = agent
            self.access_count[key] = 1
            print(f"【缓存新增】添加 Agent 实例（key：{key}）")

    def clear_agent(self, key: str) -> None:
        """删除指定的Agent实例"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                del self.access_count[key]

    def clear_all(self) -> None:
        """清空所有缓存"""
        with self.lock:
            self.cache.clear()
            self.access_count.clear()


# ---------------------------
# 初始化缓存管理器（全局单例）
# ---------------------------
agent_cache = AgentCacheManager(max_size=get_config_by_key('MAX_AGENT_CACHE_SIZE'))