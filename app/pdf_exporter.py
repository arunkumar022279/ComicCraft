from pathlib import Path
from fpdf import FPDF
from PIL import Image
import re
import uuid

EXPORT_DIR = Path("static/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def _local_path(web_path: str) -> str:
    return web_path.lstrip("/").replace("/", str(Path("/").anchor)) if False else web_path.lstrip("/")

def save_pdf(comic: dict) -> str:
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    for panel in comic["panels"]:
        pdf.add_page()
        pdf.set_fill_color(20, 20, 30)
        pdf.rect(0, 0, 297, 210, "F")

        pdf.set_text_color(255, 214, 82)
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_xy(14, 10)
        pdf.cell(0, 12, comic["title"][:45])

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_xy(14, 25)
        pdf.cell(0, 9, f"PANEL {panel['number']}  •  {panel['title'][:55]}")

        image_path = Path(panel["image"].lstrip("/"))
        if image_path.exists():
            with Image.open(image_path) as img:
                w, h = img.size
                ratio = w / h
                box_w, box_h = 265, 115
                if ratio > box_w / box_h:
                    box_h = box_w / ratio
                else:
                    box_w = box_h * ratio
            pdf.image(str(image_path), x=16, y=39, w=box_w, h=box_h)

        text_y = 39 + 115 + 4
        pdf.set_text_color(255, 214, 82)
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_xy(16, text_y)
        pdf.multi_cell(265, 5, panel["caption"][:180])

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_xy(16, text_y + 9)
        pdf.multi_cell(265, 5, panel["narration"][:500])

        if panel.get("dialogue"):
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_xy(16, 193)
            pdf.cell(265, 7, f'"{panel["dialogue"][:150]}"', align="C")

    filename = EXPORT_DIR / f"comiccraft_{uuid.uuid4().hex[:8]}.pdf"
    pdf.output(str(filename))
    return "/" + filename.as_posix()
