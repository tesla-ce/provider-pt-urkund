FROM python:3.8-alpine

# Version to use
ARG TESLA_CE_PROVIDER_VERSION

# Define the TeSLA CE package to install
ARG TESLA_CE_PROVIDER_PACKAGE="tesla-ce-provider-pt-urkund==$TESLA_CE_PROVIDER_VERSION"

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            g++ \
            gcc \
            make \
            cmake \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            libffi-dev \
	        jpeg-dev \
	        freetype-dev \
            git \
            python3-dev \
            expat-dev \
    && python3 -m venv /venv \
    && /venv/bin/pip install -U pip \
    # Install the package
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir $TESLA_CE_PROVIDER_PACKAGE" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

# Install production dependencies
RUN set -ex \
    && apk add --no-cache \
            bash \
            nano \
            gcc \
            libressl-dev \
            libffi \
            freetype \
            jpeg \
            libxml2 \
            libxslt \
            expat \
            libmagic

# Prepare environment
ENV PROVIDER_CLASS=urkund.UrkundProvider
ENV PROVIDER_VERSION=$TESLA_CE_PROVIDER_VERSION

# Create a user and group for Celery
RUN addgroup -g 2000 -S celery && \
    adduser -u 1000 -S celery -G celery

ADD docker/check_health.sh /venv/bin/check_health.sh
RUN chmod +x /venv/bin/check_health.sh

USER celery

CMD ["/venv/bin/celery", "-A", "tesla_ce_provider", "worker", "-l", "warning", "-P", "gevent", "-O", "fair"]

HEALTHCHECK --start-period=15s --retries=3 CMD "/venv/bin/check_health.sh"

ENTRYPOINT ["/venv/bin/python"]
