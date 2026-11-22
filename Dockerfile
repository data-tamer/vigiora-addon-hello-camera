# Built on the Vigiora server from this repository (run.source: build in vigiora-addon.yaml).
#
# Before you submit, pin the base image by digest so the build is repeatable:
#   docker buildx imagetools inspect python:3.12-slim-bookworm      then use  FROM python:3.12-slim-bookworm@sha256:...
FROM python:3.12-slim-bookworm

# Where the kit comes from while it has no package index entry. Change it if you use your own copy of the
# vigiora-addon-kit repository (and use a release tag, not a branch) before you build or submit.
ARG KIT_SOURCE=https://github.com/data-tamer/vigiora-addon-kit/archive/refs/tags/v0.1.0.tar.gz

RUN useradd --system --uid 10001 addon && mkdir /data && chown addon /data
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir "${KIT_SOURCE}" && pip install --no-cache-dir --no-deps .

USER addon
ENV PYTHONUNBUFFERED=1
CMD ["hello-camera"]
