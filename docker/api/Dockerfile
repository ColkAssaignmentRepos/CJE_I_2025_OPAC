FROM ubuntu:24.04

ENV APP_DIR="/app/"
ENV UV_PROJECT_ENVIRONMENT="/venv/"

# uv をインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 必要な依存関係をインストール、不要なファイルを削除
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y curl git openssh-client && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p ${APP_DIR} ${UV_PROJECT_ENVIRONMENT}

ENV PATH="${UV_PROJECT_ENVIRONMENT}/bin:$PATH"

WORKDIR ${APP_DIR}

# プロジェクトの依存関係をインストール
COPY ./README.md ./pyproject.toml ./uv.lock* ${APP_DIR}
RUN uv sync

COPY ./ ${APP_DIR}

# import で参照できるようにするため
# ./ を PYTHONPATH に追加
ENV PYTHONPATH="${APP_DIR}:${PYTHONPATH}"

ENTRYPOINT ["uv", "run", "--", "sh", "-c"]
