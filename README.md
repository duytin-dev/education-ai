# LearnHub AI

Service gia sư: giải thích bài học, sinh trắc nghiệm, chấm bài. FastAPI + LangChain — **không train model**.

Repo này **chỉ là AI**. Spring Boot gọi HTTP vào đây. Frontend **không** gọi thẳng service này.

| Service | Cổng |
|---------|------|
| AI (repo này) | 8000 |
| Backend Spring | 8080 |
| Frontend Next.js | 3000 |

## Stack

- FastAPI, Uvicorn
- LangChain
- LLM: **Gemini** (mặc định, free tier) / OpenAI / Ollama local

## Cấu trúc

```
education-ai/
├── app/
│   ├── main.py          /health  POST /explain /quiz /grade
│   ├── llm.py           Chọn provider từ .env
│   ├── chains.py        Prompt tiếng Việt, bám nội dung bài
│   └── schemas.py       Pydantic request/response
├── requirements.txt
├── .env.example
└── README.md
```

## API

| Method | Path | Body chính | Trả về |
|--------|------|------------|--------|
| GET | `/health` | — | `{ "status": "ok" }` |
| POST | `/explain` | `course_title`, `lesson_*`, `question` | `{ "answer": "..." }` |
| POST | `/quiz` | ngữ cảnh + `count` (3–10) | `{ "questions": [...] }` |
| POST | `/grade` | `questions` + `answers` | điểm, feedback |

Hết hạn mức Gemini → HTTP **429**, `detail`: `Bạn đã hết quota. Vui lòng thử lại sau.`

Spring forward từ `POST /api/v1/ai/*` (chỉ STUDENT đã ghi danh).

## Chạy

Python 3.11+.

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Sửa `.env`:

```env
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.6-flash
GOOGLE_API_KEY=AIza...
```

Key miễn phí: [Google AI Studio](https://aistudio.google.com/apikey). Free tier ~20 request/ngày/model.

```powershell
uvicorn app.main:app --reload --port 8000
```

Health: http://127.0.0.1:8000/health

## Provider khác

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Hoặc local, không cloud:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

Cài [Ollama](https://ollama.com), `ollama pull llama3.2`.

Không commit `.env`.
