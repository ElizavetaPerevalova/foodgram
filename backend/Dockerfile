FROM python:3.9

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8500

CMD ["gunicorn", "--bind", "0.0.0.0:8500", "backend.wsgi"]
