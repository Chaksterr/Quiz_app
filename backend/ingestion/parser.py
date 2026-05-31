import fitz
from pptx import Presentation


def parse_pdf(path: str) -> str:
    doc   = fitz.open(path)
    pages = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def parse_pptx(path: str) -> str:
    prs    = Presentation(path)
    slides = []
    for i, slide in enumerate(prs.slides):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                t = shape.text_frame.text.strip()
                if t:
                    texts.append(t)
        if texts:
            slides.append(f"Slide {i+1}:\n" + "\n".join(texts))
    return "\n\n".join(slides)


def parse_file(path: str, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return parse_pdf(path)
    return parse_pptx(path)
