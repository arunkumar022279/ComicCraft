from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .gemini_service import generate_comic_outline, generate_panel_image
from .pdf_exporter import save_pdf


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
    )


# ---------------------------------------------------------
# GENERATE COMIC
# ---------------------------------------------------------
@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
    panels: int = Form(5),
):
    # Keep the panel count between 3 and 6
    panel_count = max(3, min(int(panels), 6))

    # Create input object
    data = type(
        "ComicInput",
        (),
        {
            "story_prompt": story_prompt,
            "character_name": character_name,
            "setting": setting,
            "tone": tone,
            "art_style": art_style,
            "panels": panel_count,
        },
    )()

    # Generate comic story
    comic = generate_comic_outline(data)

    # Generate images for every panel
    for panel in comic["panels"]:
        panel["image"] = generate_panel_image(
            panel["image_prompt"],
            panel["number"],
            comic["title"],
        )

    # Generate PDF
    comic["pdf"] = save_pdf(comic)

    # Render preview page
    return templates.TemplateResponse(
        request,
        "comic_preview.html",
        {
            "comic": comic,
        },
    )


# ---------------------------------------------------------
# JSON API
# ---------------------------------------------------------
@router.post("/generate-comic/json")
async def generate_json(payload: dict):
    panel_count = max(
        3,
        min(int(payload.get("panels", 5)), 6),
    )

    data = type(
        "ComicInput",
        (),
        {
            "story_prompt": payload.get(
                "story_prompt",
                "A fun adventure",
            ),
            "character_name": payload.get(
                "character_name",
                "Hero",
            ),
            "setting": payload.get(
                "setting",
                "fantasy world",
            ),
            "tone": payload.get(
                "tone",
                "funny",
            ),
            "art_style": payload.get(
                "art_style",
                "cute cartoon",
            ),
            "panels": panel_count,
        },
    )()

    # Generate comic
    comic = generate_comic_outline(data)

    # Generate panel images
    for panel in comic["panels"]:
        panel["image"] = generate_panel_image(
            panel["image_prompt"],
            panel["number"],
            comic["title"],
        )

    # Generate PDF
    comic["pdf"] = save_pdf(comic)

    return JSONResponse(content=comic)


# ---------------------------------------------------------
# DOWNLOAD PDF
# ---------------------------------------------------------
@router.get("/download")
async def download_pdf(path: str):
    safe = Path(path.lstrip("/"))

    if not safe.exists():
        return JSONResponse(
            {
                "error": "PDF not found",
            },
            status_code=404,
        )

    if safe.suffix.lower() != ".pdf":
        return JSONResponse(
            {
                "error": "Invalid PDF file",
            },
            status_code=400,
        )

    return FileResponse(
        path=safe,
        media_type="application/pdf",
        filename=safe.name,
    )


# ---------------------------------------------------------
# EXPORT SUCCESS PAGE
# ---------------------------------------------------------
@router.get("/export-success")
async def export_success(request: Request):
    return templates.TemplateResponse(
        request,
        "export_success.html",
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------
@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ComicCraft",
    }