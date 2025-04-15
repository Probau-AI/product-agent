FROM python:3.12.8-slim
# declare ports which container exposess
EXPOSE 8000
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create app directory to work in
WORKDIR /app

# install uv
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

# install python requirements
# copy just dependency file(s) and install before rest of code to avoid having to
# reinstall packages during build every time code changes
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

COPY . ./

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
