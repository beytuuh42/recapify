# Recapify

AI-powered summaries of TV shows, movies, and anime. Type a free-text request like *"summarize Attack on Titan season 2 episode 3"* — Recapify parses the intent, fetches the subtitles from OpenSubtitles, and returns a compact episode summary via Gemini.

**Live demo:** https://recapify-frontend.onrender.com

> Hosted on Render free tier — the backend may take 30–60 seconds to wake up on the first request after a period of inactivity.

## Stack

| Service | Tech | Port |
|---|---|---|
| `frontend` | Angular 19 (Signals) | 4200 |
| `backend` | Spring Boot 4, Java 21, WebClient | 8080 |
| `ml` | FastAPI, LangChain, `google-genai`, `opensubtitlescom` | 8000 |

```
Browser → Angular → Spring Boot → FastAPI → OpenSubtitles + Gemini
```

## Quick start

Prerequisites: Docker Desktop, Git.

```bash
git clone <repo-url> recapify
cd recapify
cp ml/.env.example ml/.env   # then fill in API keys
docker compose --profile dev watch
```

Open http://localhost:4200.

`watch` enables hot-reload across all services — edit source files and changes apply live. Dependency files (`pom.xml`, `requirements.txt`, `package.json`) trigger a rebuild.

## API keys

In `ml/.env`:
- `GOOGLE_API_KEY` — https://aistudio.google.com/apikey
- `OPEN_SUBTITLES_API_KEY`, `OPEN_SUBTITLES_USER`, `OPEN_SUBTITLES_PASSWORD` — https://www.opensubtitles.com/

## Project layout

```
recapify/
├── frontend/              # Angular app
├── backend/recapify/      # Spring Boot app
├── ml/                    # FastAPI ML service
│   ├── app/               # Source
│   └── prompts/           # LLM prompt templates
└── docker-compose.yml
```
