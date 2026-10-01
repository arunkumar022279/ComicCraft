# ComicCraft — AI Comic Story Creator

A creative FastAPI + Jinja2 web app that turns a user's story idea into a multi-panel comic using Google's Gemini API.

## What this version includes

- FastAPI backend
- Jinja2 frontend
- Gemini structured story generation
- Gemini native image generation
- 3–6 configurable comic panels
- Cute cartoon / comic / anime-inspired / pixel / storybook / 3D styles
- Interactive prompt chips and generation progress UI
- Comic preview with expandable panels
- PDF export
- JSON API endpoint
- FastAPI Swagger docs
- `.env` API-key configuration

## 1. Open in VS Code

Open the `ComicCraft` folder in VS Code.

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows CMD:

```bat
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install packages

```bash
pip install -r requirements.txt
```

## 4. Add your Google AI API key

Copy `.env.example` to `.env` and put your key in:

```env
GEMINI_API_KEY=YOUR_KEY_HERE
```

Create/get a Gemini API key in Google AI Studio.

Do not upload `.env` to GitHub.

## 5. Run

```bash
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── models.py
│   ├── gemini_service.py
│   └── pdf_exporter.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── generated/
│   └── exports/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## API example

POST `/generate-comic/json`

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Finn",
  "setting": "Enchanted forest",
  "tone": "Adventurous",
  "art_style": "Cute cartoon",
  "panels": 5
}
```

## Notes

The original project document describes Gemini Flash + Gemini Pro for text and Stable Diffusion for images. This implementation keeps the document's five-stage workflow but uses Google's current Gemini SDK and native image-generation capability for the image stage, so one Google AI API integration can power both storytelling and illustrations.

For production, add authentication, rate limiting, persistent comic storage, background jobs, and cloud object storage.
