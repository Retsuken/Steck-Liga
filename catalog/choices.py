SPECIALIZATIONS = [
    ("backend", "Backend-разработка"),
    ("frontend", "Frontend-разработка"),
    ("fullstack", "Fullstack-разработка"),
    ("mobile", "Мобильная разработка"),
    ("devops", "DevOps / SRE"),
    ("data", "Data Science / ML"),
    ("qa", "QA / автотестирование"),
    ("security", "Информационная безопасность"),
    ("analytics", "Аналитика данных"),
]

GRADES = [
    ("intern", "Стажёр"),
    ("junior", "Junior"),
    ("middle", "Middle"),
    ("senior", "Senior"),
    ("lead", "Lead"),
]

GRADE_ORDER = {code: i for i, (code, _) in enumerate(GRADES)}

INDUSTRIES = [
    ("fintech", "Финтех"),
    ("ecommerce", "E-commerce"),
    ("saas", "SaaS / B2B"),
    ("gamedev", "Геймдев"),
    ("gov", "Госсектор"),
    ("telecom", "Телеком"),
    ("media", "Медиа и контент"),
    ("industry", "Промышленность / IoT"),
    ("edtech", "EdTech"),
    ("other", "Другое"),
]

STACK_CATALOG = [
    "Python", "Django", "FastAPI", "Flask", "Java", "Spring", "Kotlin", "Go",
    "C#", ".NET", "C++", "Rust", "Node.js", "TypeScript", "JavaScript",
    "React", "Vue", "Angular", "Next.js", "HTML", "CSS", "Svelte",
    "Swift", "Flutter", "React Native",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka",
    "Docker", "Kubernetes", "Linux", "Nginx", "CI/CD", "AWS", "GCP", "Azure",
    "Pandas", "NumPy", "PyTorch", "TensorFlow", "Spark", "SQL",
    "Pytest", "Selenium", "Playwright",
    "OWASP", "Pentest",
]

INVITE_STATUSES = [
    ("sent", "Отправлено"),
    ("viewed", "Просмотрено"),
    ("accepted", "Принято"),
    ("declined", "Отклонено"),
]

APPLICATION_STATUSES = [
    ("sent", "Отправлено"),
    ("viewed", "Просмотрено"),
    ("accepted", "Принято"),
    ("rejected", "Отклонено"),
]


def spec_label(code: str) -> str:
    return dict(SPECIALIZATIONS).get(code, code)


def grade_label(code: str) -> str:
    return dict(GRADES).get(code, code)


def category_code(spec: str, grade: str) -> str:
    return f"{spec}:{grade}"


def category_label(spec: str, grade: str) -> str:
    return f"{spec_label(spec)} · {grade_label(grade)}"
