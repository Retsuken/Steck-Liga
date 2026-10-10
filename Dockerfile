FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p data media
ENV DJANGO_DEBUG=1
EXPOSE 8000
CMD sh -c "python manage.py migrate && python manage.py seed_demo && python manage.py runserver 0.0.0.0:8000"
