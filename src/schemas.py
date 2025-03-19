from typing import Literal
from pydantic import BaseModel, Field


# ------------------------------------------------------------------------------------------------
# Response Schema
# ------------------------------------------------------------------------------------------------
class MessageOutput(BaseModel): 
    response: str


class ModerationInputGuardrailOutput(BaseModel):
    is_flagged: bool = Field(description="Your final answer.")
    error_message: Literal["Input is not flagged", "Input is flagged"] = Field(description="If the input is not flagged, return 'Input is not flagged'. If the input is flagged, return 'Input is flagged'.")


class OutputGuardrailOutput(BaseModel):
    reasoning: str = Field(description="Use this as a scratchpad to reflect for whether the output contains any non-English content.")
    is_non_english: bool = Field(description="Your final answer.")
    error_message: Literal["Output is non-English", "Output is English"] = Field(description="If the output contains any non-English content, return 'Output is non-English'. If the output contains only English content, return 'Output is English'.")


class RelevanceInputGuardrailOutput(BaseModel):
    reasoning: str = Field(description="Use this as a scratchpad to reflect for whether the input is relevant to travelling.")
    is_irrelevant: bool = Field(description="Your final answer.")
    error_message: Literal["Input is relevant", "Input is irrelevant"] = Field(description="If the input is relevant to travelling, return 'Input is relevant'. If the input is not relevant to travelling, return 'Input is irrelevant'.")


class MinLengthInputGuardrailOutput(BaseModel):
    is_too_short: bool = Field(description="Your final answer.")
    error_message: Literal["Input is long enough", "Input is too short"] = Field(description="If the input is long enough, return 'Input is long enough'. If the input is too short, return 'Input is too short'.")

