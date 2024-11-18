# docker-modx-revolution An auto-updating dockerfile to run ModX Revolution CMS
# Copyright (C) 2021  Jan Giesenberg <749@github.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

FROM php:8-fpm-alpine

LABEL org.opencontainers.image.authors="Jan Giesenberg <749@github.com>"

EXPOSE 9000

RUN apk add --no-cache rsync freetype-dev libpng-dev jpeg-dev unzip sudo bash gettext \
	&& docker-php-ext-configure gd --with-freetype --with-jpeg \
	&& docker-php-ext-install -j$(nproc) gd opcache mysqli pdo pdo_mysql \
	&& rm -rf /usr/src/php/

ARG MODX_VERSION 2.8.7
ENV MODX_VERSION ${MODX_VERSION}

# upstream tarballs include ./modx-${MODX_VERSION}/
RUN cd / \
  && echo ${MODX_VERSION} \
  && curl -o modx.zip -SL http://modx.com/download/direct/modx-${MODX_VERSION}-pl.zip \
	&& unzip -q modx.zip -d /usr/src \
	&& rm -rf /modx \
	&& mkdir -p /modx /usr/src/modx \
  && mv /usr/src/modx-${MODX_VERSION}-pl/ /modx/public \
	&& find /modx -name 'ht.access' -exec bash -c 'rm $0' {} \; \
	&& mv /modx/public/core /modx/ \
	&& cp -r /modx/public/setup /usr/src/modx \
  && rm modx.zip \
	&& chown -R www-data:www-data /modx

COPY --chown=www-data files/docker-entrypoint.sh /entrypoint.sh
COPY --chown=www-data:www-data files/docker-entrypoint /docker-entrypoint
COPY files/php-config/ /usr/local/etc/php/conf.d/
COPY --chown=www-data:www-data files/config.core.php /modx/config.core.php.tmpl

RUN chmod +x /entrypoint.sh \
	&& mkdir -p /modx/static/manager /modx/core/config /modx/core/packages /modx/core/components /modx/public/assets

VOLUME /modx/static/manager
VOLUME /modx/core/config
VOLUME /modx/core/packages
VOLUME /modx/core/components
VOLUME /modx/public/assets


WORKDIR /modx/public
ENTRYPOINT ["/entrypoint.sh"]
CMD ["php-fpm"]