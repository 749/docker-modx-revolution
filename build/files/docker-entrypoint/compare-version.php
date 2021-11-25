<?php
$currentInstallVersion = trim(file_get_contents('/modx/core/config/install_version.txt'));
if($currentInstallVersion == '') {
	echo '/modx/core/config/install_version.txt does not contain a valid version number!';
} else if (version_compare($currentInstallVersion, $argv[1]) < 0) {
	echo '1';
} else {
	echo '0';
}