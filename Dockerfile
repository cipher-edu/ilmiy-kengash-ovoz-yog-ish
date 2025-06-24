# Dockerfile

# 1. Asosiy Python image'ini tanlash
FROM python:3.11-slim

# 2. Ishchi muhit o'zgaruvchilarini sozlash
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Ishchi papka yaratish va o'rnatish
WORKDIR /app

# 4. Tizim paketlarini yangilash va kerakli kutubxonalarni o'rnatish (PostgreSQL uchun)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 5. requirements.txt faylini nusxalash va paketlarni o'rnatish
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Loyiha kodini nusxalash
COPY . .

# 7. Static fayllarni yig'ish
# Bu production uchun muhim, lekin development'da ham ishlatsa bo'ladi
RUN python manage.py collectstatic --noinput

# 8. Kerakli portni ochish (Gunicorn uchun)
EXPOSE 8000

# 9. Ilovani Gunicorn orqali ishga tushirish (production'da ishlatiladi)
# Development uchun bu buyruq docker-compose.yml'da o'zgartiriladi
CMD ["gunicorn", "ilmiy.wsgi:application", "--bind", "0.0.0.0:8000"]
