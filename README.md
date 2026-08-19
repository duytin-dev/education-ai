# LearnHub AI (LangChain)

Service gia sư: giải thích bài học, sinh trắc nghiệm, nhận xét bài làm.

Xem cấu trúc toàn LearnHub: [README gốc](../README.md).

```powershell
cd c:\LearnHub\education-ai
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Mặc định **Gemini miễn phí** (`LLM_PROVIDER=gemini`). Lấy key tại https://aistudio.google.com/apikey rồi điền `GOOGLE_API_KEY` trong `.env`.

Không muốn cloud: cài [Ollama](https://ollama.com), `ollama pull llama3.2`, đặt `LLM_PROVIDER=ollama`.

```powershell
uvicorn app.main:app --reload --port 8000
```

Health: http://127.0.0.1:8000/health

Spring gọi service này (cổng 8000). Frontend không gọi thẳng Python.
