# Банк заданий: концептуальные MCQ + параметризованные задачи.
# options для mcq: [{"key": "a", "text": "..."}]
# param: stem с {a},{b}; answer_expr; options — выражения-дистракторы.


def _mcq(spec, grade, skill, diff, stem, options, key, disc=1.0):
    return {
        "specialization": spec,
        "grade": grade,
        "skill": skill,
        "difficulty": diff,
        "qtype": "mcq",
        "stem": stem,
        "options": options,
        "answer_key": key,
        "param_spec": {},
        "answer_expr": "",
        "discrimination": disc,
    }


def _param(spec, grade, skill, diff, stem, param_spec, expr, distractors, disc=1.2):
    return {
        "specialization": spec,
        "grade": grade,
        "skill": skill,
        "difficulty": diff,
        "qtype": "param",
        "stem": stem,
        "options": distractors,
        "answer_key": "",
        "param_spec": param_spec,
        "answer_expr": expr,
        "discrimination": disc,
    }


BANK = [
    _mcq("backend", "intern", "python", 1, "Какой тип у литерала 3.14 в Python?", [
        {"key": "a", "text": "int"}, {"key": "b", "text": "float"},
        {"key": "c", "text": "decimal"}, {"key": "d", "text": "double"},
    ], "b"),
    _mcq("backend", "intern", "http", 1, "Какой код ответа означает «ресурс создан»?", [
        {"key": "a", "text": "200"}, {"key": "b", "text": "201"},
        {"key": "c", "text": "204"}, {"key": "d", "text": "301"},
    ], "b"),
    _param("backend", "intern", "python", 2,
           "Что вернёт выражение len(range({a}, {b})) в Python, если шаг равен 1?",
           {"a": {"min": 1, "max": 5}, "b": {"min": 8, "max": 14}},
           "b - a", ["a + b", "b", "a"]),
    _mcq("backend", "junior", "sql", 2, "Какая нормальная форма запрещает повторяющиеся группы?", [
        {"key": "a", "text": "1NF"}, {"key": "b", "text": "2NF"},
        {"key": "c", "text": "3NF"}, {"key": "d", "text": "BCNF"},
    ], "a", 1.1),
    _mcq("backend", "junior", "django", 2, "Что делает select_related в Django ORM?", [
        {"key": "a", "text": "JOIN для ForeignKey / OneToOne"},
        {"key": "b", "text": "Отдельные запросы для M2M"},
        {"key": "c", "text": "Кэширует весь queryset навсегда"},
        {"key": "d", "text": "Блокирует строку SELECT FOR UPDATE"},
    ], "a"),
    _param("backend", "junior", "algo", 2,
           "Сколько сравнений в худшем случае у линейного поиска по массиву из {n} элементов?",
           {"n": {"min": 7, "max": 20}}, "n", ["n-1", "n+1", "n*2"]),
    _mcq("backend", "middle", "arch", 3, "Идемпотентный метод HTTP среди перечисленных?", [
        {"key": "a", "text": "POST"}, {"key": "b", "text": "PUT"},
        {"key": "c", "text": "PATCH неидемпотентен всегда"}, {"key": "d", "text": "CONNECT"},
    ], "b", 1.3),
    _mcq("backend", "middle", "db", 3, "Что описывает уровень изоляции Repeatable Read?", [
        {"key": "a", "text": "Запрещает грязное и неповторяющееся чтение"},
        {"key": "b", "text": "Разрешает грязное чтение"},
        {"key": "c", "text": "Гарантирует отсутствие фантомов во всех СУБД одинаково"},
        {"key": "d", "text": "Это синоним autocommit"},
    ], "a", 1.4),
    _param("backend", "middle", "complex", 3,
           "Асимптотика вставки в конец динамического массива амортизированно O(?). Введите степень n: для O(n^k) укажите k. Для O(1) ответ 0. Массив растёт ×2, n={n}.",
           {"n": {"min": 8, "max": 64}}, "0", ["1", "2", "n"]),
    _mcq("backend", "senior", "dist", 4, "Что обеспечивает outbox pattern?", [
        {"key": "a", "text": "Надёжную публикацию события вместе с записью в БД"},
        {"key": "b", "text": "Шардирование кэша"},
        {"key": "c", "text": "Сжатие JSON"},
        {"key": "d", "text": "A/B тестирование API"},
    ], "a", 1.5),
    _mcq("backend", "senior", "sre", 4, "Circuit breaker в микросервисах нужен, чтобы:", [
        {"key": "a", "text": "Остановить каскадные отказы к деградировавшему сервису"},
        {"key": "b", "text": "Увеличить размер пула соединений"},
        {"key": "c", "text": "Заменить TLS"},
        {"key": "d", "text": "Сериализовать protobuf"},
    ], "a"),
    _mcq("backend", "lead", "arch", 5, "Стратегия, когда команда владеет сервисом целиком (код, прод, дежурства)?", [
        {"key": "a", "text": "You build it, you run it"},
        {"key": "b", "text": "Waterfall ownership"},
        {"key": "c", "text": "Shared nothing UI"},
        {"key": "d", "text": "Gold plating"},
    ], "a", 1.2),
    _mcq("frontend", "intern", "js", 1, "typeof null в JavaScript?", [
        {"key": "a", "text": "null"}, {"key": "b", "text": "object"},
        {"key": "c", "text": "undefined"}, {"key": "d", "text": "number"},
    ], "b"),
    _mcq("frontend", "intern", "css", 1, "Свойство для flex-контейнера, выравнивающее по главной оси?", [
        {"key": "a", "text": "align-items"}, {"key": "b", "text": "justify-content"},
        {"key": "c", "text": "flex-wrap"}, {"key": "d", "text": "order"},
    ], "b"),
    _param("frontend", "junior", "js", 2,
           "Чему равен результат: [{a}, {b}].map(x => x * 2).length ?",
           {"a": {"min": 1, "max": 9}, "b": {"min": 1, "max": 9}}, "2", ["a + b", "4", "1"]),
    _mcq("frontend", "junior", "react", 2, "Зачем нужен key в списке React?", [
        {"key": "a", "text": "Чтобы согласовать identity элементов между рендерами"},
        {"key": "b", "text": "Чтобы задать CSS-класс"},
        {"key": "c", "text": "Это обязательный HTML-атрибут браузера"},
        {"key": "d", "text": "Для SEO"},
    ], "a"),
    _mcq("frontend", "middle", "js", 3, "Что такое event loop?", [
        {"key": "a", "text": "Цикл, разбирающий очередь макро/микрозадач и колбэки"},
        {"key": "b", "text": "Бесконечный for в UI-потоке Windows"},
        {"key": "c", "text": "Алгоритм CSS containment"},
        {"key": "d", "text": "Протокол WebRTC"},
    ], "a", 1.3),
    _mcq("frontend", "middle", "web", 3, "CORS preflight — это запрос метода:", [
        {"key": "a", "text": "OPTIONS"}, {"key": "b", "text": "TRACE"},
        {"key": "c", "text": "HEAD всегда"}, {"key": "d", "text": "CONNECT"},
    ], "a"),
    _mcq("frontend", "senior", "perf", 4, "layout thrashing возникает, когда:", [
        {"key": "a", "text": "Чередуются чтение геометрии и запись стилей в одном кадре"},
        {"key": "b", "text": "Слишком мало DOM-узлов"},
        {"key": "c", "text": "Используется transform: translateZ(0)"},
        {"key": "d", "text": "Отключён gzip"},
    ], "a", 1.4),
    _mcq("frontend", "lead", "arch", 5, "Микрофронтенды оправданы, если:", [
        {"key": "a", "text": "Независимые команды и независимый релизный цикл частей UI"},
        {"key": "b", "text": "Нужно уменьшить число HTTP-запросов любой ценой"},
        {"key": "c", "text": "Проект на одном экране"},
        {"key": "d", "text": "Нет сборщика"},
    ], "a"),
    _mcq("fullstack", "junior", "http", 2, "REST-ресурс лучше идентифицировать:", [
        {"key": "a", "text": "Существительным в URI, глагол — методом HTTP"},
        {"key": "b", "text": "RPC-глаголом в каждом пути /getUser"},
        {"key": "c", "text": "Только через SOAP action"},
        {"key": "d", "text": "Случайным портом"},
    ], "a"),
    _mcq("fullstack", "middle", "auth", 3, "Access token + refresh token: access обычно:", [
        {"key": "a", "text": "Короткоживущий, refresh — длиннее и хранится бережнее"},
        {"key": "b", "text": "Бессрочный в localStorage"},
        {"key": "c", "text": "Пароль пользователя в Base64"},
        {"key": "d", "text": "То же, что CSRF-токен формы"},
    ], "a"),
    _mcq("fullstack", "senior", "obs", 4, "Три столпа observability:", [
        {"key": "a", "text": "Логи, метрики, трейсы"},
        {"key": "b", "text": "CPU, RAM, диск"},
        {"key": "c", "text": "Dev, staging, prod"},
        {"key": "d", "text": "REST, GraphQL, gRPC"},
    ], "a"),
    _mcq("mobile", "junior", "android", 2, "Activity уничтожается при повороте, если не обработан configChanges. Состояние UI сохраняют через:", [
        {"key": "a", "text": "ViewModel / savedInstanceState"},
        {"key": "b", "text": "Только static поля"},
        {"key": "c", "text": "Thread.sleep"},
        {"key": "d", "text": "JNI"},
    ], "a"),
    _mcq("mobile", "middle", "ios", 3, "Main thread в iOS отвечает за:", [
        {"key": "a", "text": "UI и касания; сеть лучше уводить в фон"},
        {"key": "b", "text": "Только компиляцию Swift"},
        {"key": "c", "text": "Только Bluetooth"},
        {"key": "d", "text": "APNS шифрование"},
    ], "a"),
    _mcq("devops", "junior", "linux", 2, "Какой сигнал обычно просит процесс завершиться корректно?", [
        {"key": "a", "text": "SIGKILL"}, {"key": "b", "text": "SIGTERM"},
        {"key": "c", "text": "SIGSTOP"}, {"key": "d", "text": "SIGPIPE всегда"},
    ], "b"),
    _mcq("devops", "middle", "k8s", 3, "liveness probe перезапускает контейнер, readiness:", [
        {"key": "a", "text": "Убирает под из Service до готовности принимать трафик"},
        {"key": "b", "text": "Удаляет namespace"},
        {"key": "c", "text": "Масштабирует HPA"},
        {"key": "d", "text": "Выпускает сертификат"},
    ], "a", 1.3),
    _mcq("devops", "senior", "sre", 4, "Error budget связан с:", [
        {"key": "a", "text": "SLO: допустимая доля ошибок/простоя до остановки релизов"},
        {"key": "b", "text": "Размером AWS bill"},
        {"key": "c", "text": "Числом docker pull"},
        {"key": "d", "text": "Версией Terraform"},
    ], "a"),
    _mcq("data", "junior", "sql", 2, "GROUP BY нужен, чтобы:", [
        {"key": "a", "text": "Агрегировать строки по ключу"},
        {"key": "b", "text": "Создать индекс"},
        {"key": "c", "text": "Заменить WHERE"},
        {"key": "d", "text": "Включить WAL"},
    ], "a"),
    _mcq("data", "middle", "ml", 3, "Переобучение видно, если:", [
        {"key": "a", "text": "Ошибка на train низкая, на validation высокая"},
        {"key": "b", "text": "Обе ошибки одинаково низкие"},
        {"key": "c", "text": "Модель линейная"},
        {"key": "d", "text": "Используется dropout"},
    ], "a", 1.3),
    _param("data", "junior", "stat", 2,
           "Среднее арифметическое чисел {a} и {b}?",
           {"a": {"min": 4, "max": 20}, "b": {"min": 4, "max": 20}},
           "(a + b) / 2", ["a - b", "a * b", "a"]),
    _mcq("data", "senior", "ml", 4, "Data leakage — это:", [
        {"key": "a", "text": "Информация из будущего/теста протекла в обучение"},
        {"key": "b", "text": "Утечка паролей из S3"},
        {"key": "c", "text": "Dropout слишком большой"},
        {"key": "d", "text": "Мало GPU"},
    ], "a"),
    _mcq("qa", "junior", "test", 2, "Пирамида тестов снизу вверх:", [
        {"key": "a", "text": "Unit → integration → e2e"},
        {"key": "b", "text": "e2e → unit → ручные"},
        {"key": "c", "text": "Только UI"},
        {"key": "d", "text": "Только нагрузка"},
    ], "a"),
    _mcq("qa", "middle", "auto", 3, "Flaky-тест — это тест, который:", [
        {"key": "a", "text": "То проходит, то падает без изменения кода"},
        {"key": "b", "text": "Всегда красный"},
        {"key": "c", "text": "Проверяет только CSS"},
        {"key": "d", "text": "Запущен в Safari"},
    ], "a"),
    _mcq("security", "junior", "owasp", 2, "SQL-инъекция предотвращается в первую очередь:", [
        {"key": "a", "text": "Параметризованными запросами / ORM"},
        {"key": "b", "text": "Скрытием схемы в UI"},
        {"key": "c", "text": "HTTP/2"},
        {"key": "d", "text": "Minification JS"},
    ], "a"),
    _mcq("security", "middle", "web", 3, "XSS отражённый отличается от хранимого тем, что:", [
        {"key": "a", "text": "Полезная нагрузка приходит в запросе и сразу отражается"},
        {"key": "b", "text": "Это то же, что CSRF"},
        {"key": "c", "text": "Работает только в XML"},
        {"key": "d", "text": "Нужен корневой доступ к ОС"},
    ], "a"),
    _mcq("analytics", "junior", "metric", 2, "Конверсия — это:", [
        {"key": "a", "text": "Доля пользователей, совершивших целевое действие"},
        {"key": "b", "text": "Число сессий"},
        {"key": "c", "text": "Размер выборки A/A"},
        {"key": "d", "text": "CAC в рублях"},
    ], "a"),
    _mcq("analytics", "middle", "exp", 3, "p-value — это:", [
        {"key": "a", "text": "Вероятность увидеть такие или более крайние данные при верной H0"},
        {"key": "b", "text": "Вероятность, что H1 истинна"},
        {"key": "c", "text": "Доля конверсии"},
        {"key": "d", "text": "Мощность теста всегда"},
    ], "a", 1.4),
]
