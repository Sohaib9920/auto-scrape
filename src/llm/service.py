from pydantic import BaseModel
from typing import Literal, TypeVar
from litellm import completion


AvailableModel = Literal[
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4o-2024-08-06",
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
]


class ChatCompletionResponseMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


ResponseModel = TypeVar(
    "ResponseModel", bound=BaseModel
)  # to make output class reference input class. type[BaseModel] for both input and ouput has not reference


class LLM:
    def __init__(self, model: AvailableModel):
        self.model = model

    def create_chat_completion(
        self, messages: list[dict[str, str]], response_model: ResponseModel
    ) -> ResponseModel:

        response = completion(
            model=self.model,
            messages=messages,
            response_format=response_model,
            stream=False,
        )

        content: str = response.choices[0].message.content
        return response_model.model_validate_json(content)
