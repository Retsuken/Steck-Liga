from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from candidates.models import CandidateProfile, Experience, FspAchievement, GradeHistory
from catalog.choices import STACK_CATALOG
from employers.models import Company, HiringNeed
from matching.models import Invitation
from testing.models import EmployerChallenge, Question
from testing.question_bank import BANK
from vacancies.models import Application, Vacancy

PASS = "hackathon2026"


class Command(BaseCommand):
    help = "Демо-данные для СтекЛиги"

    def handle(self, *args, **opts):
        if Question.objects.exists():
            self.stdout.write("Данные уже загружены (есть вопросы). Пропуск.")
            return
        for item in BANK:
            Question.objects.create(**item)

        def cand(email, name, spec, grade, score, stack, city, years, fsp_id="", fsp=None, about=""):
            u = User.objects.create_user(
                email=email, password=PASS, role=User.Role.CANDIDATE,
                email_confirmed=True, consent_pd=True, consent_at=timezone.now(),
            )
            p = CandidateProfile.objects.create(
                user=u, full_name=name, phone="+7 900 111-22-33", city=city,
                about=about or "Ищу сильную инженерную команду.",
                stack=stack, soft_skills=["коммуникация", "ownership", "менторство"][:2],
                years_experience=years, industry="saas", specialization=spec,
                claimed_grade=grade, confirmed_grade=grade, last_test_score=score,
                last_grade_change_at=timezone.now(), freshness_score=70,
                fsp_id=fsp_id, publish_profile=True, consent_publish=True,
            )
            Experience.objects.create(profile=p, company="Прошлый работодатель", role=spec, years=years)
            GradeHistory.objects.create(
                profile=p, specialization=spec, from_grade="", to_grade=grade,
                score=score, note="Демо: категория присвоена",
            )
            for row in fsp or []:
                FspAchievement.objects.create(profile=p, **row)
            return p

        p1 = cand(
            "anna@demo.ru", "Анна Волкова", "backend", "middle", 88,
            ["Python", "Django", "PostgreSQL", "Redis", "Docker"], "Екатеринбург", 3.5,
            fsp_id="FSP-10482",
            fsp=[
                {"event_name": "Кубок ФСП по алгоритмам", "year": 2025, "place": 7, "rating_points": 210, "discipline": "алгоритмы"},
                {"event_name": "Хакатон ФСП Ural", "year": 2024, "place": 2, "rating_points": 160, "discipline": "продукт"},
            ],
            about="Бэкенд на Django/PostgreSQL, люблю чистые API и наблюдаемость.",
        )
        cand(
            "ivan@demo.ru", "Иван Петров", "frontend", "junior", 71,
            ["JavaScript", "TypeScript", "React", "CSS", "HTML"], "Москва", 0.8,
            about="Фронтенд, собираю интерфейсы на React. Истории ФСП нет.",
        )
        cand(
            "maria@demo.ru", "Мария Соколова", "backend", "senior", 93,
            ["Python", "FastAPI", "PostgreSQL", "Kafka", "Kubernetes"], "Санкт-Петербург", 7,
            fsp_id="FSP-22011",
            fsp=[{"event_name": "Чемпионат ФСП, финал", "year": 2025, "place": 3, "rating_points": 340, "discipline": "алгоритмы"}],
        )
        cand(
            "dmitry@demo.ru", "Дмитрий Орлов", "devops", "middle", 80,
            ["Linux", "Docker", "Kubernetes", "CI/CD", "Nginx"], "Новосибирск", 4,
            fsp_id="FSP-08812",
            fsp=[{"event_name": "DevOps-спринт ФСП", "year": 2025, "place": 12, "rating_points": 90, "discipline": "инфра"}],
        )
        cand(
            "elena@demo.ru", "Елена Кузнецова", "data", "junior", 76,
            ["Python", "Pandas", "SQL", "PyTorch"], "Казань", 1.2,
            fsp_id="FSP-33190",
            fsp=[{"event_name": "ML Battle ФСП", "year": 2026, "place": 15, "rating_points": 70, "discipline": "ML"}],
        )
        cand(
            "pavel@demo.ru", "Павел Новиков", "frontend", "middle", 84,
            ["TypeScript", "React", "Next.js", "CSS"], "Москва", 4,
        )
        cand(
            "olga@demo.ru", "Ольга Белова", "qa", "middle", 79,
            ["Pytest", "Playwright", "Python", "CI/CD"], "Самара", 3,
        )
        cand(
            "kirill@demo.ru", "Кирилл Морозов", "mobile", "junior", 68,
            ["Kotlin", "Flutter"], "Пермь", 1,
            about="Мобильная разработка. Профиль без ФСП.",
        )
        cand(
            "sergey@demo.ru", "Сергей Лебедев", "backend", "intern", 64,
            ["Python", "Django", "SQL"], "Тюмень", 0.3,
        )
        cand(
            "alina@demo.ru", "Алина Фролова", "fullstack", "senior", 91,
            ["TypeScript", "React", "Node.js", "PostgreSQL", "Docker"], "Москва", 6,
            fsp_id="FSP-15002",
            fsp=[{"event_name": "ФСП Fullstack Cup", "year": 2025, "place": 5, "rating_points": 180, "discipline": "fullstack"}],
        )

        eu = User.objects.create_user(
            email="hr@severcode.ru", password=PASS, role=User.Role.EMPLOYER,
            email_confirmed=True, consent_pd=True, consent_at=timezone.now(),
        )
        c1 = Company.objects.create(
            user=eu, name="ООО «Северный код»",
            description="Продуктовая компания: B2B-платформа для промышленной аналитики.",
            industry="industry", city="Екатеринбург", site="https://severcode.example",
            phone="+7 343 000-11-22", contact_email="hr@severcode.ru",
        )
        eu2 = User.objects.create_user(
            email="jobs@datapotok.ru", password=PASS, role=User.Role.EMPLOYER,
            email_confirmed=True, consent_pd=True, consent_at=timezone.now(),
        )
        c2 = Company.objects.create(
            user=eu2, name="АО «ДатаПоток»",
            description="Обработка потоковых данных и ML-сервисы.",
            industry="saas", city="Москва", contact_email="jobs@datapotok.ru",
        )

        n1 = HiringNeed.objects.create(
            company=c1, title="Backend Middle в платформу телеметрии",
            team_about="Команда из 6 человек, сервисы на Django и очередях.",
            description="Нужен разработчик API, PostgreSQL, опыт промышленных интеграций.",
            specialization="backend", grade="middle",
            stack=["Python", "Django", "PostgreSQL", "Redis"],
            salary_from=220000, salary_to=300000,
        )
        HiringNeed.objects.create(
            company=c2, title="Junior DS в команду рекомендаций",
            team_about="Небольшая ML-группа, фичи и офлайн-метрики.",
            description="SQL, pandas, базовый PyTorch.",
            specialization="data", grade="junior",
            stack=["Python", "Pandas", "SQL", "PyTorch"],
            salary_from=130000, salary_to=180000,
        )

        v1 = Vacancy.objects.create(
            company=c1, title="Frontend Middle (React)",
            description="Кабинет оператора телеметрии, сложные таблицы и графики.",
            specialization="frontend", grade="middle",
            stack=["TypeScript", "React", "CSS"],
            salary_from=200000, salary_to=280000, city="Екатеринбург", remote=True,
        )
        Vacancy.objects.create(
            company=c2, title="Data Scientist Junior",
            description="Фичи, витрины, эксперименты.",
            specialization="data", grade="junior",
            stack=["Python", "SQL", "Pandas"],
            salary_from=140000, salary_to=190000, city="Москва", remote=True,
        )
        Vacancy.objects.create(
            company=c1, title="Backend Senior",
            description="Архитектура сервисов ingest, Kafka, SLO.",
            specialization="backend", grade="senior",
            stack=["Python", "Kafka", "PostgreSQL", "Kubernetes"],
            salary_from=350000, salary_to=480000, city="Екатеринбург", remote=True,
        )

        EmployerChallenge.objects.create(
            company=c1, title="Спроектируйте идемпотентный ingest API",
            prompt="Коротко опишите, как примете пачку событий с at-least-once доставкой и не запишете дубли. Стек: HTTP + PostgreSQL.",
            specialization="backend", grade="middle",
        )
        EmployerChallenge.objects.create(
            company=c2, title="Метрика качества ранжирования",
            prompt="Какую офлайн-метрику возьмёте для выдачи рекомендаций и почему не ограничитесь accuracy?",
            specialization="data", grade="junior",
        )

        Invitation.objects.create(
            company=c1, candidate=p1, need=n1,
            offer_text="Приглашаем в команду телеметрии: Django API, on-call 1 раз в 6 недель, удалёнка.",
            salary_from=240000, salary_to=290000,
            contact_method="telegram @severcode_hr · hr@severcode.ru",
        )
        Application.objects.create(
            vacancy=v1, candidate=CandidateProfile.objects.get(user__email="pavel@demo.ru"),
            cover_letter="Делал кабинеты со сложными таблицами на React.",
        )

        admin = User.objects.create_superuser(
            email="admin@stekliga.local", password=PASS, role=User.Role.EMPLOYER, email_confirmed=True, consent_pd=True
        )
        Company.objects.get_or_create(user=admin, defaults={"name": "СтекЛига", "contact_email": admin.email})
        self.stdout.write(self.style.SUCCESS(
            "Готово. Кандидат: anna@demo.ru / hackathon2026 · Работодатель: hr@severcode.ru / hackathon2026"
        ))
        _ = STACK_CATALOG
