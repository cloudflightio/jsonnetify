FROM debian:bullseye-slim as base

ENV \
    POETRY_VERSION=1.1.15 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

COPY ["poetry.lock", "pyproject.toml", "/var/app/"]

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y \
        python3.9 \
        python3-pip \
    && cd /var/app \
    && pip install "poetry==$POETRY_VERSION" \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && rm -rf /var/cache/apt/archives

COPY "src/" "/var/app/"

WORKDIR /var/app

ENTRYPOINT [ "python3", "-m", "jsonnetify" ]

FROM base as compressor

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y \
        python3.9-dev \
        build-essential \
        ccache \
        clang \
        libfuse-dev \
        upx \
        patchelf \
    && python3.9 -m pip install nuitka orderedset

RUN python3.9 -m nuitka \
        --standalone \
        --nofollow-import-to=pytest \
        --python-flag=nosite,-O \
        --plugin-enable=anti-bloat,implicit-imports,data-files,pylint-warnings \
        --clang \
        --warn-implicit-exceptions \
        --warn-unusual-code \
        --prefer-source-code \
        jsonnetify

WORKDIR /var/app/jsonnetify.dist/

RUN ldd jsonnetify | grep "=> /" | awk '{print $3}' | xargs -I '{}' cp --no-clobber -v '{}' . \
    && ldd jsonnetify | grep "/lib64/ld-linux-x86-64" | awk '{print $1}' | xargs -I '{}' cp --parents -v '{}' . \
    && cp --no-clobber -v /lib/x86_64-linux-gnu/libgcc_s.so.1 . \
    && mkdir -p ./lib/x86_64-linux-gnu/ \
    && cp --no-clobber -v /lib/x86_64-linux-gnu/libresolv* ./lib/x86_64-linux-gnu \
    && cp --no-clobber -v /lib/x86_64-linux-gnu/libnss_dns* ./lib/x86_64-linux-gnu 

RUN upx -9 jsonnetify

FROM scratch 

COPY --from=compressor /var/app/jsonnetify.dist/ /

ENTRYPOINT [ "/jsonnetify" ]
