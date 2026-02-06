import pathlib
from typing import Any, Dict, Optional


from system.utils import get_project_path
import yaml


def loadSkill(skill_path: str):
    """
    这里后面可以根据 metadata 加载 Skill，这里暂时留空。
    """
    pass


def parseMetadataFromSkill(skill_path: pathlib.Path) -> Optional[Dict[str, Any]]:
    """
    从 Skill.md 中解析 YAML 元数据（front matter），返回 dict。

    期望格式大致如下（front matter 必须在文件最开头）：

    ---
    name: xxx
    description: yyy
    tags:
      - a
      - b
    ---

    后面跟正文内容。
    """
    skill_file = pathlib.Path(skill_path).joinpath("Skill.md")

    if not skill_file.exists():
        raise FileNotFoundError(f"Skill.md 不存在: {skill_file}")

    text = skill_file.read_text(encoding="utf-8")

    # 按行手动查找 front matter 的起止位置
    lines = text.splitlines()
    if not lines:
        raise ValueError("Skill.md Metadata加载异常： 文件内容为空。")

    # front matter 必须从第一行的 '---' 开始
    if lines[0].strip() != "---":
        raise ValueError("Skill.md Metadata加载异常： 没有找到开始的 '---'。")

    end_index: Optional[int] = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break

    if end_index is None:
        # 没有找到结束的 '---'
        raise ValueError("Skill.md Metadata加载异常： 中的 front matter 没有结束。")

    yaml_lines = lines[1:end_index]
    yaml_text = "\n".join(yaml_lines)

    try:
        metadata = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"解析 Skill.md 中 YAML 元数据失败: {e}")

    if not isinstance(metadata, dict):
        raise ValueError("Skill.md 中 YAML 元数据的根节点必须是一个对象（mapping）。")

    # 补充skill_metadata信息
    if "location" not in metadata:
        metadata["location"]=skill_file.as_posix()
    return metadata

def get_skill_xml_template(skill_metadata:dict)->str:
    """
    根据 skill_metadata 生成 skill 的 xml 模板
    :param skill_metadata:
    :return:
    """
    xml_template=f"""
<available_skills>
  <skill>
    <name>{skill_metadata["name"]}</name>
    <description>{skill_metadata["description"]}</description>
    <location>{skill_metadata["location"]}</location>
  </skill>
</available_skills>
"""
    xml_template = xml_template.strip()
    return xml_template

def get_skills_xml_template(skill_metadata_list:list[dict])->str:
    if not skill_metadata_list:
        return ""
    # 初始化skill子节点的拼接容器
    skill_nodes = []
    # 循环遍历，生成每个skill节点并加入列表
    for skill_metadata in skill_metadata_list:
        skill_node = f"""
          <skill>
            <name>{skill_metadata["name"]}</name>
            <description>{skill_metadata["description"]}</description>
            <location>{skill_metadata["location"]}</location>
          </skill>
        """
        skill_nodes.append(skill_node)

    # 拼接所有子节点，再包裹根节点（join会自动拼接列表所有元素，保留格式）
    xml_template = f"""
    <available_skills>
    {''.join(skill_nodes)}
    </available_skills>
    """
    # 可选：清理多余的首尾空白（避免XML有大量空行，根据需求选择）
    xml_template = xml_template.strip()
    return xml_template


if __name__ == '__main__':
    project_path = get_project_path()
    skills_path = project_path.joinpath("system/skills")
    print(parseMetadataFromSkill(skills_path.joinpath("test_skill")))