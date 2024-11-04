FROM python:alpine

RUN apk fix && \
    apk --no-cache --update add git

RUN git config --global user.name "getdocsy[Bot]" # TODO remove hardcoded bot name and make it depend on environment
RUN git config --global user.email "171265091+getdocsy[bot]@users.noreply.github.com"

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

COPY docsy docsy

RUN poetry install --without dev

ENTRYPOINT ["poetry", "run", "gunicorn", "-w", "1", "-b", "0.0.0.0:3000", "docsy.slack.slack:flask_app"]
