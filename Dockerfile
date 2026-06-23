FROM python:3.13-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY src2/ ./src2/

EXPOSE 8001

CMD ["poetry", "run", "uvicorn", "src2.main:app", "--host", "0.0.0.0", "--port", "8001"]