# השתמש בדמות פייתון רשמית
FROM python:3.13-slim-bookworm

# הגדרת תיקיית העבודה בתוך המכולה
WORKDIR /app

# העתקת קובץ הדרישות והתקנתן
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# העתקת כל שאר קבצי הקוד לתוך המכולה
COPY . .

# הגדרת משתנה סביבה לפורט (Cloud Run משתמש ב-8080 כברירת מחדל)
ENV PORT 8080

# הפקודה להרצת השרת באמצעות gunicorn (שרת מקצועי)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 server:app