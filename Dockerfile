FROM debian:buster-slim

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

ENV LANG C.UTF-8

RUN set -x; \
        apt-get update \
        && apt install --fix-broken \
        && apt-get install -y --no-install-recommends \
                ca-certificates \
                wget \
                git \
                curl \
                make \
                dirmngr \
                fonts-noto-cjk \
                gnupg \
                libssl-dev \
                node-less \
                npm \
                python3-num2words \
                python3-pdfminer \
                python3-pip \
                python3-phonenumbers \
                python3-pyldap \
                python3-qrcode \
                python3-renderpm \
                python3-setuptools \
                python3-slugify \
                python3-vobject \
                python3-watchdog \
                python3-xlrd \
                python3-xlwt \
                python3-numpy \
                python3-boto3 \
                python3-requests \
                python3-xmltodict \
                python3-pandas \
                python3-holidays \
                xz-utils \
        && curl -o wkhtmltox.deb -sSL https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.stretch_amd64.deb \
        && echo '7e35a63f9db14f93ec7feeb0fce76b30c08f2057 wkhtmltox.deb' | sha1sum -c - \
        && apt-get install -y --no-install-recommends ./wkhtmltox.deb \
        && rm -rf /var/lib/apt/lists/* wkhtmltox.deb

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
    && GNUPGHOME="$(mktemp -d)" \
    && export GNUPGHOME \
    && repokey='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8' \
    && gpg --batch --keyserver keyserver.ubuntu.com --recv-keys "${repokey}" \
    && gpg --batch --armor --export "${repokey}" > /etc/apt/trusted.gpg.d/pgdg.gpg.asc \
    && gpgconf --kill all \
    && rm -rf "$GNUPGHOME" \
    && apt-get update \
    && apt-get install --no-install-recommends -y postgresql-client \
    && rm -f /etc/apt/sources.list.d/pgdg.list \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g rtlcss

ENV ODOO_VERSION 14.0
ARG ODOO_RELEASE=20201002
ARG ODOO_SHA=70917e1db8d100c791f31afbfcd782dd026bd4c9
RUN curl -o odoo.deb -sSL http://nightly.odoo.com/${ODOO_VERSION}/nightly/deb/odoo_${ODOO_VERSION}.${ODOO_RELEASE}_all.deb \
    && echo "${ODOO_SHA} odoo.deb" | sha1sum -c - \
    && apt-get update \
    && apt-get -y install --no-install-recommends ./odoo.deb \
    && rm -rf /var/lib/apt/lists/* odoo.deb

#install libraries adds

RUN pip3 install email-validator
RUN pip3 install python-barcode
RUN pip3 install pypng
RUN pip3 install PyQRCode
RUN apt-get update && apt-get install -y build-essential gcc
RUN apt-get update && apt-get install -y python3-dev libffi-dev
RUN pip3 install --upgrade pip setuptools
RUN pip3 install pyopenssl
RUN pip3 install pysftp

COPY ./entrypoint.sh /
COPY ./odoo.conf /etc/odoo/

RUN ["chmod", "+x", "./entrypoint.sh"]

RUN chown odoo /etc/odoo/odoo.conf \
    && mkdir -p /mnt/extra-addons \
    && chown -R odoo /mnt/extra-addons  

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo/odoo.conf

# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]

CMD ["odoo"]