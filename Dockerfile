# Built on the Vigiora server from this repository (run.source: build in vigiora-addon.yaml).
#
# The server accepts a Dockerfile only when every FROM is pinned by digest (and there is no "# syntax=" line unless
# it is pinned too), so the build is repeatable. This is the multi-arch index of python:3.12-slim-bookworm
# (linux/amd64 and linux/arm64). To refresh it:
#   docker buildx imagetools inspect python:3.12-slim-bookworm      and copy the "Digest:" line of the index
FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

# Where the kit comes from while it has no package index entry. Change it if you use your own copy of the
# vigiora-addon-kit repository (and use a release tag, not a branch) before you build or submit.
ARG KIT_SOURCE=https://github.com/data-tamer/vigiora-addon-kit/archive/refs/tags/v0.2.0.tar.gz

RUN useradd --system --uid 10001 addon && mkdir /data && chown addon /data
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir "${KIT_SOURCE}" && pip install --no-cache-dir --no-deps .

USER addon
ENV PYTHONUNBUFFERED=1
CMD ["hello-camera"]
