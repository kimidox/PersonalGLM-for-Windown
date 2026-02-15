import base64
import os
from datetime import datetime
from io import BytesIO

import pyautogui
from langchain_core.tools import tool


@tool(description="获取当前屏幕的截屏，返回图片的本地文件路径")
def get_local_screenshot_path() -> str:
    """
    获取当前屏幕截屏，保存到本地并返回文件路径
    返回值：图片的绝对路径（方便智能体读取）
    """
    # 截取屏幕
    screen = pyautogui.screenshot()
    # 生成唯一文件名
    file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_path = f"./static/{file_name}.png"
    # 保存图片
    screen.save(file_path)
    # 返回绝对路径（推荐）
    abs_path = os.path.abspath(file_path)
    return f"截图已保存，路径：{abs_path}"

@tool(description="获取当前屏幕的截屏，返回图片的Base64编码字符串")
def get_local_screenshot_base64() -> str:
    """
    获取当前屏幕截屏，返回Base64编码的图片字符串
    适合需要直接传输图片内容的场景（如API调用、无文件系统的环境）
    """
    # 截取屏幕
    screen = pyautogui.screenshot()
    # 将图片存入内存流
    buffer = BytesIO()
    screen.save(buffer, format="PNG")
    # 转为Base64编码
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    # 返回Base64字符串（可直接用于HTML/img标签或解码还原图片）
    return f"data:image/png;base64,{img_base64}"

@tool(description="获取指定城市的天气信息")
def get_weather_for_location(city: str) -> str:
    return f"{city}是天气晴朗的!"



# @tool
# def get_user_location() -> str:
#     """Retrieve user information based on user ID."""
#     user_id = runtime.context.user_id
#     return "Florida" if user_id == "1" else "SF"