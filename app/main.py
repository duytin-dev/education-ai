from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.chains import explain, generate_quiz, grade_quiz
from app.schemas import (
    ExplainRequest,
    ExplainResponse,
    GradeRequest,
    GradeResponse,
    QuizRequest,
    QuizResponse,
)

app = FastAPI(title="LearnHub AI Tutor", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_quota_error(ex: Exception) -> bool:
    text = str(ex).lower()
    return (
        "resource_exhausted" in text
        or "insufficient_quota" in text
        or "quota exceeded" in text
        or "exceeded your current quota" in text
        or "generate_content_free_tier" in text
    )


def raise_ai_http(ex: Exception) -> None:
    if is_quota_error(ex):
        raise HTTPException(
            status_code=429,
            detail="Bạn đã hết quota. Vui lòng thử lại sau.",
        ) from ex
    if isinstance(ex, RuntimeError):
        raise HTTPException(status_code=503, detail=str(ex)) from ex
    raise HTTPException(status_code=502, detail=f"AI lỗi: {ex}") from ex


def parse_body(request: Request, model):
    raw = request.state.raw_body if hasattr(request.state, "raw_body") else None
    if raw is None:
        raise HTTPException(status_code=422, detail="Không đọc được JSON body")
    if not raw:
        raise HTTPException(
            status_code=422,
            detail=(
                "Body rỗng. content-type="
                f"{request.headers.get('content-type')} "
                f"content-length={request.headers.get('content-length')}"
            ),
        )
    try:
        return model.model_validate_json(raw)
    except ValidationError as ex:
        raise HTTPException(status_code=422, detail=ex.errors()) from ex


@app.middleware("http")
async def cache_body(request: Request, call_next):
    request.state.raw_body = await request.body()
    return await call_next(request)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/explain", response_model=ExplainResponse)
async def api_explain(request: Request):
    req = parse_body(request, ExplainRequest)
    try:
        return ExplainResponse(answer=explain(req))
    except Exception as ex:
        raise_ai_http(ex)


@app.post("/quiz", response_model=QuizResponse)
async def api_quiz(request: Request):
    req = parse_body(request, QuizRequest)
    try:
        return generate_quiz(req)
    except Exception as ex:
        raise_ai_http(ex)


@app.post("/grade", response_model=GradeResponse)
async def api_grade(request: Request):
    req = parse_body(request, GradeRequest)
    try:
        return grade_quiz(req)
    except Exception as ex:
        raise_ai_http(ex)
