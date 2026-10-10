from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _font():
    candidates = [
        Path(r"C:\Windows\Fonts\arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    ]
    for p in candidates:
        if p.exists():
            pdfmetrics.registerFont(TTFont("Body", str(p)))
            return "Body"
    return "Helvetica"


def build_profile_pdf(profile) -> bytes:
    font = _font()
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 20 * mm
    c.setFillColorRGB(0.04, 0.12, 0.23)
    c.rect(0, h - 28 * mm, w, 28 * mm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont(font, 16)
    c.drawString(18 * mm, h - 14 * mm, "СтекЛига · стандартизированный профиль")
    c.setFont(font, 10)
    c.drawString(18 * mm, h - 21 * mm, "Верифицированная категория и достижения ФСП")
    y = h - 40 * mm
    c.setFillColorRGB(0.05, 0.07, 0.12)
    c.setFont(font, 18)
    c.drawString(18 * mm, y, profile.full_name or "Кандидат")
    y -= 10 * mm
    c.setFont(font, 11)
    lines = [
        f"Категория: {profile.category_label}",
        f"Город: {profile.city or '—'}",
        f"Стаж: {profile.years_experience} лет",
        f"Результат теста: {profile.last_test_score}%",
        f"Стек: {', '.join(profile.stack or []) or '—'}",
        f"Софт-скиллы: {', '.join(profile.soft_skills or []) or '—'}",
        f"ФСП ID: {profile.fsp_id or 'не привязан'}",
    ]
    for line in lines:
        c.drawString(18 * mm, y, line[:110])
        y -= 7 * mm
    y -= 4 * mm
    c.setFont(font, 12)
    c.drawString(18 * mm, y, "Достижения ФСП")
    y -= 8 * mm
    c.setFont(font, 10)
    if not profile.achievements.exists():
        c.drawString(18 * mm, y, "История участия в мероприятиях ФСП отсутствует.")
        y -= 7 * mm
    else:
        for a in profile.achievements.all()[:12]:
            place = f", место {a.place}" if a.place else ""
            c.drawString(18 * mm, y, f"{a.year} · {a.event_name}{place} · {a.rating_points} очков")
            y -= 6 * mm
            if y < 25 * mm:
                c.showPage()
                y = h - 20 * mm
    y -= 6 * mm
    c.setFont(font, 12)
    c.drawString(18 * mm, y, "О себе")
    y -= 8 * mm
    c.setFont(font, 10)
    about = (profile.about or "—").replace("\n", " ")
    while about:
        c.drawString(18 * mm, y, about[:100])
        about = about[100:]
        y -= 6 * mm
    c.setFont(font, 8)
    c.drawString(18 * mm, 12 * mm, "Контакты скрыты до принятия приглашения работодателем.")
    c.save()
    return buf.getvalue()
