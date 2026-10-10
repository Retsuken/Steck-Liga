from django.core.management.base import BaseCommand
from employers.models import HiringNeed
from matching.engine import match_candidates


class Command(BaseCommand):
    help = "Процедура валидации подбора на демо-данных"

    def handle(self, *args, **opts):
        need = HiringNeed.objects.filter(specialization="backend", grade="middle").first()
        if not need:
            self.stderr.write("Сначала python manage.py seed_demo")
            return
        ranked = match_candidates(need)
        top = [r["profile"].full_name for r in ranked[:3]]
        self.stdout.write("Топ-3 по потребности Backend Middle:")
        for r in ranked[:5]:
            self.stdout.write(f"  {r['score']:5.1f}  {r['profile'].full_name}  {r['category']}")
        relevant = {"Анна Волкова", "Мария Соколова", "Сергей Лебедев"}
        # intern тоже backend, но слабее; релевантный топ — middle/senior
        gold_top = {"Анна Волкова", "Мария Соколова"}
        hit = len(gold_top & set(top)) / 2
        p3 = len([n for n in top if n in gold_top | relevant]) / max(1, len(top))
        self.stdout.write(f"Доля эталонных middle/senior в топ-3 (полнота пары): {hit:.2f}")
        self.stdout.write(f"precision@3 по backend-метке: {p3:.2f}")
        names = [r["profile"].full_name for r in ranked]
        if "Иван Петров" in names:
            pos = names.index("Иван Петров") + 1
            self.stdout.write(f"Frontend без пересечения специализации: позиция {pos} (должен быть низко или отсутствовать)")
        no_fsp = [r for r in ranked if not r["profile"].has_fsp]
        self.stdout.write(f"Кандидаты без ФСП в выдаче: {len(no_fsp)} (не отбрасываются)")
