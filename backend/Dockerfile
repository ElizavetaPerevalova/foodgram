# FROM python:3.9

# WORKDIR /app

# COPY . /app/

# RUN pip install --no-cache-dir -r requirements.txt

# EXPOSE 8500

# CMD ["gunicorn", "--bind", "0.0.0.0:8500", "backend.wsgi"]
FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r /app/requirements.txt --no-cache-dir

COPY ingredients.csv data/
COPY ingredients.json data/
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8500", "backend.wsgi"]