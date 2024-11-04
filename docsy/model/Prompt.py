from typing import TypedDict, Literal

class Prompt(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

