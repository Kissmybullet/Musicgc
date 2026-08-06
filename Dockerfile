FROM alpine:3.22 AS python-builder

ARG PYTHON_VERSION=3.11.15

RUN apk add --no-cache \
    build-base \
    ca-certificates \
    wget \
    xz \
    openssl-dev \
    bzip2-dev \
    zlib-dev \
    readline-dev \
    sqlite-dev \
    ncurses-dev \
    gdbm-dev \
    xz-dev \
    libffi-dev \
    tk-dev

WORKDIR /usr/src

RUN wget -q https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz \
    && tar -xzf Python-${PYTHON_VERSION}.tgz \
    && cd Python-${PYTHON_VERSION} \
    && ./configure --prefix=/opt/python --with-ensurepip=install \
    && make -j"$(nproc)" \
    && make install

FROM alpine:3.22

RUN apk add --no-cache \
    ffmpeg \
    git \
    curl \
    ca-certificates \
    libstdc++ \
    glib \
    mesa-gl \
    openssl \
    bzip2 \
    zlib \
    readline \
    sqlite-libs \
    ncurses-libs \
    gdbm \
    xz-libs \
    libffi \
    tk

COPY --from=python-builder /opt/python /opt/python

ENV PATH="/opt/python/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

RUN python3.11 -m pip install --no-cache-dir --upgrade pip uv

WORKDIR /app
COPY . .

RUN uv pip install -e . --system

CMD ["python3.11", "-m", "src"]
