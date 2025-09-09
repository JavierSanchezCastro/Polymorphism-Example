from typing import Annotated, Literal
from pydantic import BaseModel, Field

class OptionBase(BaseModel):
    id: int
    text: str
    is_correct: bool

class QuestionBase(BaseModel):
    id: int
    type: str  # 'open', 'exact', 'multiple_choice', 'true_false'

class OpenQuestion(QuestionBase):
    type: Literal["open"]
    question_text: str

class ExactQuestion(QuestionBase):
    type: Literal["exact"]
    question_text: str
    exact_answer: str

class MultipleChoiceQuestion(QuestionBase):
    type: Literal["multiple_choice"]
    question_text: str
    options: list[OptionBase]

class TrueFalseQuestion(QuestionBase):
    type: Literal["true_false"]
    question_text: str
    answer: bool

QuestionUnion = Annotated[OpenQuestion | ExactQuestion | MultipleChoiceQuestion | TrueFalseQuestion, Field(discriminator="type")]