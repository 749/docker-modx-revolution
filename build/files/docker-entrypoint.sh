#!/usr/bin/env bash
set -ex

PATH_MODX_CORE=/modx/core
PATH_MODX_PUBLIC=/modx/public
PATH_MODX_SETUP=/modx/public/setup
PATH_MODX_CORE_CONFIG_PHP=/modx/config.core.php.tmpl

setup_config_core() {
	cd $PATH_MODX_PUBLIC
	find -name "config.core.php" | while read line ; do
		rm $line;
		cp $PATH_MODX_CORE_CONFIG_PHP $line
	done
}

if [[ "$1" == apache2* ]] || [ "$1" == php-fpm ]; then
	if [ -n "$MYSQL_PORT_3306_TCP" ]; then
		if [ -z "$MODX_DB_HOST" ]; then
			MODX_DB_HOST='mysql'
		else
			echo >&2 'warning: both MODX_DB_HOST and MYSQL_PORT_3306_TCP found'
			echo >&2 "  Connecting to MODX_DB_HOST ($MODX_DB_HOST)"
			echo >&2 '  instead of the linked mysql container'
		fi
	fi

	if [ -z "$MODX_DB_HOST" ]; then
		echo >&2 'error: missing MODX_DB_HOST and MYSQL_PORT_3306_TCP environment variables'
		echo >&2 '  Did you forget to --link some_mysql_container:mysql or set an external db'
		echo >&2 '  with -e MODX_DB_HOST=hostname:port?'
		exit 1
	fi

	# if we're linked to MySQL and thus have credentials already, let's use them
	: ${MODX_DB_USER:=${MYSQL_ENV_MYSQL_USER:-root}}
	if [ "$MODX_DB_USER" = 'root' ]; then
		: ${MODX_DB_PASSWORD:=$MYSQL_ENV_MYSQL_ROOT_PASSWORD}
	fi
	: ${MODX_DB_PASSWORD:=$MYSQL_ENV_MYSQL_PASSWORD}
	: ${MODX_DB_NAME:=${MYSQL_ENV_MYSQL_DATABASE:-modx}}

	if [ -z "$MODX_DB_PASSWORD" ]; then
		echo >&2 'error: missing required MODX_DB_PASSWORD environment variable'
		echo >&2 '  Did you forget to -e MODX_DB_PASSWORD=... ?'
		echo >&2
		echo >&2 '  (Also of interest might be MODX_DB_USER and MODX_DB_NAME.)'
		exit 1
	fi

	TERM=dumb php -- "$MODX_DB_HOST" "$MODX_DB_USER" "$MODX_DB_PASSWORD" "$MODX_DB_NAME" </docker-entrypoint/create-database.php

	setup_config_core

	if ! [ -e index.php -a -e ../core/config/config.inc.php ]; then
		echo "MODX not installed yet, installing..." >&2

		touch /modx/core/config/config.inc.php
		chown -R www-data:www-data /modx

		: ${MODX_ADMIN_USER:='admin'}
		: ${MODX_ADMIN_PASSWORD:='admin'}

		envsubst >setup/config.xml </docker-entrypoint/install.xml

		chown www-data:www-data setup/config.xml

    sudo -u www-data php setup/index.php --installmode=new

		echo "$MODX_VERSION" >/modx/core/config/install_version.txt

		setup_config_core
		
		echo "Complete! MODX has been successfully installed" >&2
  else
		UPGRADE=$(TERM=dumb php -- "$MODX_VERSION" </docker-entrypoint/compare-version.php)

		if [ "$UPGRADE" -eq "1" ]; then
			echo >&2 "Upgrading MODX..."

			if [ ! -d "$PATH_MODX_SETUP" ]; then
				sudo -u www-data mkdir "$PATH_MODX_SETUP"

				tar cf - --one-file-system -C /usr/src/modx/setup . | tar xf - -C $PATH_MODX_SETUP

				setup_config_core
			fi

			envsubst > config.xml </docker-entrypoint/upgrade.xml

			chown -R www-data:www-data /modx

			sudo -u www-data php setup/index.php --installmode=upgrade

			echo "$MODX_VERSION" >/modx/core/config/install_version.txt

			setup_config_core

			echo "Complete! MODX has been successfully upgraded to $MODX_VERSION" >&2
		elif [ "$UPGRADE" -eq "0" ]; then
			echo "ModX already up to date."
		else
			echo "Unexpected version check output: $UPGRADE"
		fi
	fi
fi

#export static files
chown -R www-data:www-data /modx
cd /modx/public
rm -rf setup/

rsync -a --exclude='*.php' manager /modx/static


echo "Starting up $@"
exec "$@"
