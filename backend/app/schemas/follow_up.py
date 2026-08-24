from pydantic import BaseModel, Field, field_validator


class FollowUpGenerateIn(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)


class FollowUpQuestionsOut(BaseModel):
    session_id: str
    questions: list[str]
    demo_mode: bool


class FollowUpAnswer(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    answer: str = Field(default="", max_length=2000)

    @field_validator("question", "answer")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class FollowUpAnswersIn(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    answers: list[FollowUpAnswer] = Field(min_length=1, max_length=10)
