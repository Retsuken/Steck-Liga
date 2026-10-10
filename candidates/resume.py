import re
from catalog.choices import STACK_CATALOG

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
NAME_RE = re.compile(r"^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?$", re.M)


def extract_pdf_text(uploaded) -> str:
    from pypdf import PdfReader

    reader = PdfReader(uploaded)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)


def parse_resume_text(text: str) -> dict:
    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    name = ""
    for line in text.splitlines():
        line = line.strip()
        if NAME_RE.match(line):
            name = line
            break
    found_stack = []
    low = text.lower()
    for skill in STACK_CATALOG:
        if skill.lower() in low:
            found_stack.append(skill)
    years = 0
    m = re.search(r"(\d+[.,]?\d*)\s*(?:лет|года|год)\s*(?:опыта|стажа)?", text, re.I)
    if m:
        years = float(m.group(1).replace(",", "."))
    return {
        "full_name": name,
        "email": emails[0] if emails else "",
        "phone": phones[0] if phones else "",
        "stack": found_stack,
        "years_experience": years,
        "about": text[:1200],
    }
