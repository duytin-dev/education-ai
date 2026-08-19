from pydantic import BaseModel, Field


class LessonContext(BaseModel):
    course_title: str = ""
    lesson_title: str = ""
    lesson_content: str = ""
    level: str = "BEGINNER"


class ExplainRequest(LessonContext):
    question: str = Field(..., min_length=1)


class ExplainResponse(BaseModel):
    answer: str


class QuizRequest(LessonContext):
    count: int = Field(default=5, ge=3, le=10)


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: list[str]
    correctIndex: int
    explain: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]


class GradeAnswer(BaseModel):
    id: int
    selectedIndex: int


class GradeRequest(LessonContext):
    questions: list[QuizQuestion]
    answers: list[GradeAnswer]


class GradeDetail(BaseModel):
    id: int
    correct: bool
    comment: str


class GradeResponse(BaseModel):
    score: int
    correctCount: int
    total: int
    feedback: str
    details: list[GradeDetail]
