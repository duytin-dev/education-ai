from langchain_core.prompts import ChatPromptTemplate

from app.llm import get_llm
from app.schemas import (
    ExplainRequest,
    GradeRequest,
    GradeResponse,
    QuizQuestion,
    QuizRequest,
    QuizResponse,
)

SYSTEM = (
    "Bạn là gia sư lập trình IT trên LearnHub. Trả lời bằng tiếng Việt, rõ ràng, có ví dụ code khi cần. "
    "Ưu tiên bám nội dung bài học được cung cấp. Không bịa API/framework không có trong bài."
)


def _context(req) -> str:
    content = (req.lesson_content or "").strip() or "(Chưa có nội dung chi tiết, hãy giải thích theo tiêu đề bài.)"
    return (
        f"Khóa học: {req.course_title}\n"
        f"Bài học: {req.lesson_title}\n"
        f"Trình độ: {req.level}\n"
        f"Nội dung bài:\n{content}"
    )


def _message_text(result) -> str:
    """Gemini 3+ trả content dạng list block, không phải str."""
    text = getattr(result, "text", None)
    if isinstance(text, str) and text.strip():
        return text
    content = result.content if hasattr(result, "content") else result
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        joined = "".join(parts).strip()
        if joined:
            return joined
    return str(content)


def explain(req: ExplainRequest) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM),
            (
                "human",
                "Ngữ cảnh bài học:\n{context}\n\nCâu hỏi của học viên:\n{question}\n\nHãy giải thích để học viên hiểu và áp dụng được.",
            ),
        ]
    )
    chain = prompt | get_llm(0.4)
    result = chain.invoke({"context": _context(req), "question": req.question})
    return _message_text(result)


def generate_quiz(req: QuizRequest) -> QuizResponse:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM),
            (
                "human",
                "Ngữ cảnh bài học:\n{context}\n\n"
                "Tạo đúng {count} câu trắc nghiệm (mỗi câu 4 đáp án, đúng 1). "
                "correctIndex là chỉ số 0-3. explain là lý do đáp án đúng, ngắn.",
            ),
        ]
    )
    llm = get_llm(0.5).with_structured_output(QuizResponse)
    chain = prompt | llm
    quiz: QuizResponse = chain.invoke({"context": _context(req), "count": req.count})
    questions = []
    for i, q in enumerate(quiz.questions[: req.count], start=1):
        options = (q.options or [])[:4]
        while len(options) < 4:
            options.append("—")
        correct = q.correctIndex if 0 <= q.correctIndex < 4 else 0
        questions.append(
            QuizQuestion(
                id=i,
                question=q.question,
                options=options,
                correctIndex=correct,
                explain=q.explain,
            )
        )
    return QuizResponse(questions=questions)


def grade_quiz(req: GradeRequest) -> GradeResponse:
    selected = {item.id: item.selectedIndex for item in req.answers}
    payload = []
    for q in req.questions:
        payload.append(
            {
                "id": q.id,
                "question": q.question,
                "options": q.options,
                "correctIndex": q.correctIndex,
                "explain": q.explain,
                "selectedIndex": selected.get(q.id, -1),
            }
        )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM),
            (
                "human",
                "Ngữ cảnh bài học:\n{context}\n\n"
                "Kết quả làm bài (JSON):\n{payload}\n\n"
                "Chấm điểm thang 100, nhận xét từng câu, chỉ ra phần cần học lại.",
            ),
        ]
    )
    llm = get_llm(0.2).with_structured_output(GradeResponse)
    chain = prompt | llm
    return chain.invoke({"context": _context(req), "payload": payload})
