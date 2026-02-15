from langchain_deepseek import ChatDeepSeek

from system.utils import get_config_by_key

# llm=CustomChatLLM(
#     model="deepseek-v3.2",
#     temperature=0,
#     max_tokens=256,
#     top_p=1,
#     openai_api_key=get_config_by_key("API_KEY"),
#     openai_api_base=get_config_by_key("API_BASE"),
#     verbose=False,
#     streaming=True,
#     extra_body={
#         "enable_thinking": True
#     }
# )

llm=ChatDeepSeek(
    model="deepseek-v3.2",
    temperature=0,
    max_tokens=30000,
    top_p=1,
    api_key=get_config_by_key("API_KEY"),
    api_base=get_config_by_key("API_BASE"),
    verbose=True,
    streaming=False
)

if __name__ == "__main__":
    # print(llm.invoke("你好"),end="",flush=True)
    if llm.streaming:
        for chunk in llm.stream("列出唐朝三位开国功臣"):
            if chunk.content:
                print(chunk.content,end="",flush=True)
            if 'thinking_process' in chunk.additional_kwargs and chunk.additional_kwargs['thinking_process']:
                # print(chunk.additional_kwargs['thinking_process'],end="",flush=True)
                pass
    else:
        print(llm.invoke("列出唐朝三位开国功臣"))