FROM python:3.12-slim

WORKDIR /app

COPY  /user_bridge/dist/user_bridge-1.0.0.tar.gz /app/

RUN pip install poetry

RUN tar -xf user_bridge-1.0.0.tar.gz && rm user_bridge-1.0.0.tar.gz

WORKDIR /app/user_bridge-1.0.0

RUN poetry install --no-dev

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["poetry", "run", "start"]