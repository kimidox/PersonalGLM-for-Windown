from json import JSONDecodeError
from typing import Any, Iterator, Literal

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk, ChatResult, ChatGeneration
from langchain_core.runnables import Runnable
from langchain_openai import OpenAI
from langchain_openai.chat_models.base import BaseChatOpenAI, _DictOrPydanticClass, _DictOrPydantic
from pydantic import Field


class CustomChatLLM(BaseChatOpenAI):

    max_tokens: int | None = Field(default=None, alias="max_completion_tokens")
    """Maximum number of tokens to generate."""

    @property
    def lc_secrets(self) -> dict[str, str]:
        """Mapping of secret environment variables."""
        return {"api_key": "API_KEY"}



    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        try:
            client = OpenAI(
                # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
                api_key=self.openai_api_key.get_secret_value(),
                base_url=self.openai_api_base,

            )
            messages=self.convert_messages_to_deepseek_messages( messages)
            completion  = client.chat.completions.create(
                model=self.model_name,  # 您可以按需更换为其它深度思考模型
                messages=messages,
                extra_body=self.extra_body,
                stream=False,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            reasoning_content = ""
            answer_content = ""
            usage_info = {}
            # 提取完整的思考过程和回答内容
            if hasattr(completion.choices[0].message, "reasoning_content"):
                reasoning_content = completion.choices[0].message.reasoning_content or ""

            answer_content = completion.choices[0].message.content or ""

            # 获取使用信息
            if hasattr(completion, 'usage'):
                usage_info = completion.usage.model_dump()

            # 创建ChatGeneration对象
            generation = ChatGeneration(
                message=AIMessage(
                    content=answer_content,
                    additional_kwargs={
                        "thinking_process": reasoning_content,
                        "finish_reason": completion.choices[0].finish_reason if hasattr(completion,
                                                                                        'choices') else None,
                    }
                ),
                generation_info={
                    "model": run_manager.metadata["ls_model_name"],
                    "usage": usage_info,
                    "thinking_process": reasoning_content,
                    "finish_reason": completion.choices[0].finish_reason if hasattr(completion, 'choices') else None,
                }
            )

            # 创建ChatResult对象
            chat_result = ChatResult(
                generations=[generation],
                llm_output={
                    "thinking_process": reasoning_content,
                    "model": run_manager.metadata["ls_model_name"],
                    "usage": usage_info,
                    "finish_reason": completion.choices[0].finish_reason if hasattr(completion, 'choices') else None,
                }
            )

            return chat_result
        except JSONDecodeError as e:
            msg = (
                "DeepSeek API returned an invalid response. "
                "Please check the API status and try again."
            )
            raise JSONDecodeError(
                msg,
                e.doc,
                e.pos,
            ) from e

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        try:
            client = OpenAI(
                # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
                api_key=self.openai_api_key.get_secret_value(),
                base_url=self.openai_api_base,
            )
            messages=self.convert_messages_to_deepseek_messages( messages)
            completion  = client.chat.completions.create(
                model=self.model_name,  # 您可以按需更换为其它深度思考模型
                messages=messages,
                extra_body=self.extra_body,
                stream=True,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )

            # 迭代处理每个流式chunk
            for chunk in completion:
                # 跳过空chunk
                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                # 提取当前chunk的内容和思考过程
                content = choice.delta.content or ""
                reasoning_content = getattr(choice.delta, "reasoning_content", "") or ""
                finish_reason = choice.finish_reason
                generation_info={}
                # 【关键】如果需要在生成时直接打印，添加这行（强制刷新缓冲区）
                # if content:
                #     print(content, end="", flush=True)  # end="" 不换行，flush=True 强制刷新

                if finish_reason:
                    generation_info["model"] = self.model_name
                    generation_info["chunk_index"] = choice.index
                else:
                    generation_info["chunk_index"] = choice.index  # 仅携带必要的chunk索引

                # 生成并返回ChatGenerationChunk
                yield ChatGenerationChunk(
                    message=AIMessageChunk(  # 替换为AIMessageChunk
                        content=content,
                        additional_kwargs={
                            "thinking_process": reasoning_content,
                            "finish_reason": finish_reason,
                        }
                    ),
                    generation_info=generation_info
                )
        except JSONDecodeError as e:
            msg = (
                "DeepSeek API returned an invalid response. "
                "Please check the API status and try again."
            )
            raise JSONDecodeError(
                msg,
                e.doc,
                e.pos,
            ) from e

    def convert_messages_to_deepseek_messages(self, messages: list[BaseMessage]) -> list[dict]:
        """Convert messages to DeepSeek messages."""
        deepseek_messages = []
        for message in messages:
            if message.type == "human":
                deepseek_messages.append({"role": "user", "content": message.content})
            elif message.type == "ai":
                deepseek_messages.append({"role": "assistant", "content": message.content})
            elif message.type == "system":
                deepseek_messages.append({"role": "system", "content": message.content})
        return deepseek_messages
    def with_structured_output(
        self,
        schema: _DictOrPydanticClass | None = None,
        *,
        method: Literal["function_calling", "json_mode", "json_schema"] = "json_schema",
        include_raw: bool = False,
        strict: bool | None = None,
        **kwargs: Any,
    ) -> Runnable[LanguageModelInput, _DictOrPydantic]:
        return super().with_structured_output(
            schema, method=method, include_raw=include_raw, strict=strict, **kwargs
        )


