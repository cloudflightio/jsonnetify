

FROM python:3.10-alpine

ENV \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.15

# Copy only requirements to cache them in docker layer
WORKDIR /work
COPY poetry.lock pyproject.toml /work/

# Project initialization:
RUN pip install "poetry==$POETRY_VERSION" \
  && poetry config virtualenvs.create false \
  && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi

COPY src/ /work/
ENTRYPOINT [ "python", "-m", "jsonnetify" ]
