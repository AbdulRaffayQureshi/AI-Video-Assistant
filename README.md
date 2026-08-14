# 🌿 AI Meeting Assistant

Turn any YouTube video or local recording into a searchable, structured meeting digest — transcript, summary, action items, key decisions, open questions, and a RAG-powered chat interface to ask follow-up questions.

**Live demo:** [ai-video-assistant-yt-meeting.streamlit.app](https://ai-video-assistant-yt-meeting.streamlit.app/)

---

## What it does

Point it at a YouTube URL or a local audio/video file, and it will:

1. Pull and preprocess the audio
2. Transcribe it (English or Hinglish)
3. Generate a title and a structured summary
4. Extract action items, key decisions, and open questions
5. Build a retrieval-augmented (RAG) index over the transcript so you can chat with the meeting afterward

Two front ends ship with the same pipeline: a CLI (`main.py`) for quick local runs, and a Streamlit app (`app.py`) with a custom "paper-craft" UI for a friendlier, shareable experience.

---

## Pipeline

```
Source (YouTube URL or local file)
        │
        ▼
utils/audio_processor.py   →  process_input()
        │  downloads / loads audio, splits into processable chunks
        ▼
core/transcriber.py        →  transcribe_all()
        │  Whisper-based speech-to-text, language-aware (english / hinglish)
        ▼
core/summarize.py          →  generate_title(), summarize()
        │  produces a session title + structured summary
        ▼
core/extractor.py          →  extract_action_items(), extract_key_decisions(), extract_questions()
        │  pulls structured insights out of the raw transcript
        ▼
core/rag_engine.py         →  build_rag_chain(), ask_question()
        │  chunks + embeds the transcript into a vector store for retrieval
        ▼
Chat interface — ask follow-up questions grounded in the transcript
```

Every stage is a discrete, swappable module — you can drop in a different transcription backend or LLM provider without touching the rest of the pipeline.

---

## Tech stack

| Layer | Tool |
|---|---|
| Audio ingestion | `yt-dlp` (YouTube) + local file support |
| Transcription | Whisper |
| Summarization / extraction / RAG | LangChain orchestration over an LLM (Mistral) |
| Vector store | ChromaDB |
| Frontend | Streamlit |
| Config | `python-dotenv` for API keys / secrets |

---

## Project structure

```
video_agent/
├── main.py                  # CLI entry point
├── app.py                   # Streamlit UI ("Meeting Sprout")
├── requirements.txt
├── .env                     # API keys (not committed)
├── utils/
│   └── audio_processor.py   # process_input()
└── core/
    ├── transcriber.py       # transcribe_all()
    ├── summarize.py         # summarize(), generate_title()
    ├── extractor.py         # extract_action_items(), extract_key_decisions(), extract_questions()
    └── rag_engine.py        # build_rag_chain(), ask_question()
```

---

## The UI — "Meeting Sprout"

The Streamlit front end uses a custom soft, natural, "paper-craft" design rather than Streamlit's defaults:

- **Palette** — warm cream background with sage, sky-blue, blush, and sun-gold accents, color-coding each output type (summary, action items, decisions, questions)
- **Type** — Fraunces (serif, warm/organic) for headings, Nunito Sans (rounded) for body text
- **3D depth** — cards lift and tilt slightly on hover via layered CSS shadows; buttons have a real pressable/skeuomorphic feel
- **Pipeline status** — each stage (audio → transcript → title → summary → extraction → RAG) "sprouts" a growing/glowing indicator in the sidebar as it completes
- **Chat tab** — RAG-grounded Q&A over the transcript, styled as soft message bubbles

---

## Running it locally

**1. Clone and set up the environment**

```bash
git clone <your-repo-url>
cd video_agent
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

**2. Add your secrets**

Create a `.env` file in the project root with whatever API keys your `core/` modules expect (e.g. Mistral / LLM provider key). Never commit this file.

**3. Run the CLI**

```bash
python main.py
```

**4. Run the Streamlit app**

```bash
streamlit run app.py
```

---

## Deployment

Deployed on **Streamlit Community Cloud**, connected directly to the GitHub repo. Secrets (`.env` contents) are configured under the app's **Settings → Secrets** in TOML format so `load_dotenv()` / `os.environ` calls resolve the same way they do locally.

> **Note:** the pipeline's dependencies (Whisper, transformers-adjacent tooling, ChromaDB) are relatively heavy. If you fork this and hit memory limits on the free tier, Hugging Face Spaces or Render are worth considering as alternatives — they tend to offer more headroom for ML workloads.

---

## Roadmap ideas

- [ ] Support additional languages beyond English/Hinglish
- [ ] Export summary + action items as a downloadable PDF/DOCX
- [ ] Multi-meeting search across a saved history
- [ ] Speaker diarization in the transcript view