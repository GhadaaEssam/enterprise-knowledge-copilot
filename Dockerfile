FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./

COPY eval_data ./eval_data

RUN uv sync --frozen --no-dev

COPY src ./src
COPY app ./app
COPY data ./data
COPY eval_data ./eval_data

EXPOSE 8501

CMD ["uv","run","streamlit","run","app/streamlit_app.py","--server.address=0.0.0.0","--server.port=8501"]

