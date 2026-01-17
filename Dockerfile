FROM python:3.11
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

ENV FLASK_APP=app.app:app

EXPOSE 5000

ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]