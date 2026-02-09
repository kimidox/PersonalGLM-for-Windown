import os
import re
from pathlib import Path


class SkillResourceLoader:
    """智能体技能资源加载器：从Skill.md解析元数据并加载对应资源"""

    def __init__(self, skill_md_path: str):
        """
        初始化加载器
        :param skill_md_path: Skill.md文件的路径（绝对/相对路径）
        """
        self.skill_md_path = Path(skill_md_path).resolve()
        self.skill_dir = self.skill_md_path.parent  # Skill.md所在目录
        self.resource_paths = {}  # 存储解析出的资源路径元数据

    def parse_skill_md(self) -> dict:
        """
        解析Skill.md文件，提取资源文件路径元数据
        假设Skill.md中元数据格式：
        ---
        resources:
          data_file: ./data/skills.json
          model_file: ./models/skill_model.pth
          config_file: config.yaml
        ---
        """
        try:
            # 读取Skill.md内容
            with open(self.skill_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取YAML格式的元数据块（常见的md元数据格式）
            meta_pattern = r'---\n(.*?)\n---'
            meta_match = re.search(meta_pattern, content, re.DOTALL)

            if not meta_match:
                raise ValueError("Skill.md中未找到元数据块（---包裹的内容）")

            # 解析元数据中的资源路径（简化版YAML解析，也可以用pyyaml库）
            meta_content = meta_match.group(1)
            lines = [line.strip() for line in meta_content.split('\n') if line.strip()]

            # 提取resources下的路径
            in_resources = False
            for line in lines:
                if line.startswith('resources:'):
                    in_resources = True
                    continue
                if in_resources and (line.startswith('-') or ':' in line):
                    # 解析 key: path 格式
                    if ':' in line:
                        key, path = line.split(':', 1)
                        key = key.strip()
                        path = path.strip().strip('"\'')
                        # 拼接完整路径（基于Skill.md所在目录）
                        full_path = self.skill_dir / Path(path)
                        self.resource_paths[key] = full_path.resolve()

            return self.resource_paths

        except Exception as e:
            print(f"解析Skill.md失败：{e}")
            return {}

    def load_resource(self, resource_key: str, mode: str = 'r') -> any:
        """
        根据资源key加载对应的文件
        :param resource_key: 元数据中的资源名称（如data_file）
        :param mode: 打开模式（r=文本，rb=二进制）
        :return: 文件内容/对象
        """
        # 如果还没解析元数据，先解析
        if not self.resource_paths:
            self.parse_skill_md()

        # 检查资源是否存在
        if resource_key not in self.resource_paths:
            raise FileNotFoundError(f"资源 {resource_key} 未在Skill.md中定义")

        resource_path = self.resource_paths[resource_key]
        if not resource_path.exists():
            raise FileNotFoundError(f"资源文件不存在：{resource_path}")

        # 加载资源
        try:
            if mode == 'r':
                with open(resource_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif mode == 'rb':
                with open(resource_path, 'rb') as f:
                    return f.read()
            else:
                raise ValueError(f"不支持的打开模式：{mode}")
        except Exception as e:
            raise RuntimeError(f"加载资源失败：{e}")


# ===================== 示例使用 =====================
if __name__ == "__main__":
    # 1. 初始化加载器（指定Skill.md路径）
    loader = SkillResourceLoader("./Skill.md")

    # 2. 解析元数据（可选，load_resource会自动触发）
    resource_paths = loader.parse_skill_md()
    print("解析出的资源路径：", resource_paths)

    # 3. 加载指定资源
    try:
        # 加载文本类资源（如JSON/配置文件）
        data_content = loader.load_resource("data_file", mode='r')
        print("加载的data_file内容：", data_content[:100])  # 打印前100个字符

        # 加载二进制类资源（如模型文件/图片）
        # model_content = loader.load_resource("model_file", mode='rb')

    except Exception as e:
        print(f"加载资源出错：{e}")