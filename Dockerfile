FROM alpine:edge

RUN \
    apk add --no-cache bash curl python3 py3-pip go musl-dev git && \
    apk add kubectl --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ && \
    python3 -m pip install --user pipx && \
    python3 -m pipx ensurepath && \
    python3 -m pipx install yaml2jsonnet && \
    go install github.com/google/go-jsonnet/cmd/jsonnet@latest && \
    go install github.com/patrickdappollonio/kubectl-slice@latest && \
    mkdir /work

WORKDIR /work
COPY generate.sh /usr/local/bin/

ENV PATH="${PATH}:/root/go/bin:/root/.local/bin"
ENTRYPOINT [ "generate.sh" ]
