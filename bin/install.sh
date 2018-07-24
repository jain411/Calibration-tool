#!/bin/bash
# nanoREV installation/upgradation script

ROOT=
BIN_DIR=${ROOT}/usr/local/bin
EXE_PATH=${BIN_DIR}/sim7
LOGFILE_DIR=${ROOT}/var/log/SiM721
LOGFILE=${LOGFILE_DIR}/sim721_installer.log
INSTALL_DIR=${ROOT}/usr/local/stm/SiM721
NOW=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${INSTALL_DIR}_$NOW"
OLD_SETTINGS_DIR="${BACKUP_DIR}"/log
NEW_SETTINGS_DIR="${INSTALL_DIR}"/log
DESKTOP_DIR="${HOME}/Desktop"

backup_previous_installation(){

	echo "Taking backup to ${BACKUP_DIR}"
	mv ${INSTALL_DIR} ${BACKUP_DIR}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi
}

check_n_backup_previous_installation(){

	echo "================================"
	echo "Backing up previous installation"
	echo "================================"

	if [ -d ${INSTALL_DIR} ]; then

		backup_previous_installation
		Z_SUCCESS=${PIPESTATUS}
		if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi
	else
		echo "No previous installation found. Skipping backup ..."
	fi

	echo ""
}

get_source_path(){

	MY_PATH="`dirname \"$0\"`"   # relative
	MY_PATH="${MY_PATH}/.."      # Sources reside one level higher
	MY_PATH="`( cd \"${MY_PATH}\" && pwd )`"  # absolutized and normalized
	eval "$1=${MY_PATH}"         # Uses first argument as return value
}

deploy_current_installation(){

	echo "=================================="
	echo "Deploying current installation ..."
	echo "=================================="

	SRC_PATH=''
	get_source_path SRC_PATH

	# Creates installation folder
	echo "Creating folder ${INSTALL_DIR}"
	mkdir -p ${INSTALL_DIR}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	# Copy source files
	echo "Copying source files from ${SRC_PATH} to ${INSTALL_DIR}"
	cp -r ${SRC_PATH}/* ${INSTALL_DIR}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	# Set permission to all files to 644
	echo "Setting file permissions to 644 in ${INSTALL_DIR}"
	find ${INSTALL_DIR} -type f -exec chmod 644 {} +
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	# Set permission to all folders to 755
	echo "Setting folder permissions to 755 in ${INSTALL_DIR}"
	find ${INSTALL_DIR} -type d -exec chmod 755 {} +
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	restore_previous_settings
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	# Delete svn related folders
	echo "Deleting svn related folders from ${INSTALL_DIR}"
	find ${INSTALL_DIR} -name ".svn" -exec rm -rf {} +
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	set_logfiles_permissions
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	set_usb_port_permissions
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	echo ""

}

set_logfiles_permissions() {
	# Changing log files permissions to write mode 
	echo "================================================================"
	echo "Setting log and dump folder permissions to 777 in ${INSTALL_DIR}"
	echo "================================================================"

	QV_DIR=${INSTALL_DIR}/utilities/qv
	chmod 777 ${INSTALL_DIR}/log ${INSTALL_DIR}/dump -R
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	chmod 777 ${QV_DIR}/log ${QV_DIR}/dump -R
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi
	
	echo ""

}

set_usb_port_permissions() {
	RULE_FILE_nanoREV="/etc/udev/rules.d/50-ttyusb.rules"
	if [[ ! -f "${RULE_FILE_nanoREV}" ]]; then
		echo "================================================"
		echo "Changing permissions of USB ports of nanoREV ..."
		echo "================================================"

		echo KERNEL==\"ttyUSB[0-9]*\",NAME=\"tts/USB%n\",SYMLINK+=\"%k\",GROUP=\"uucp\",MODE=\"0666\" > "${RULE_FILE_nanoREV}"
		Z_SUCCESS=${PIPESTATUS}
		if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi
	else
		echo "nanoREV USB port permissions already set..."
	fi
	echo ""

	RULE_FILE_LIA="/etc/udev/rules.d/99-libftdi.rules"
	if [[ ! -f "${RULE_FILE_LIA}" ]]; then
		echo "============================================="
		echo "Changing permissions of USB ports for LIA ..."
		echo "============================================="

		echo SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6001\", MODE=\"0664\", GROUP=\"plugdev\" > ${RULE_FILE_LIA}
		Z_SUCCESS=${PIPESTATUS}
		if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi
	else
		echo "LIA USB port permissions already set..."
	fi

	echo ""
}

restore_previous_settings(){

	echo "==========================================="
	echo "Restoring previous installation settings..."
	echo "==========================================="

	if [ -d ${OLD_SETTINGS_DIR} ]; then

		cp ${OLD_SETTINGS_DIR}/* ${NEW_SETTINGS_DIR}/
		Z_SUCCESS=${PIPESTATUS}
		if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	else
		echo "No previous installation settings found. Skipping restore ..."
	fi

	echo ""
}
create_launcher(){

	echo "===================="
	echo "Creating laucher    "
	echo "===================="

	echo "Creating folder ${BIN_DIR}"
	mkdir -p ${BIN_DIR}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	echo "Creating launcher ${EXE_PATH}"
	echo "python ${INSTALL_DIR}/main.py" > ${EXE_PATH}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	echo "Setting launcher permission to 755"
	chmod 755 ${EXE_PATH}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	echo "Copying latest manual to the Desktop..."
	if [ -d ${DESKTOP_DIR} ]; then
		cp ${INSTALL_DIR}/docs/*.pdf ${DESKTOP_DIR}/
	fi
	echo ""
}

do_installation(){

	echo ""
	echo "++++++++++++++++++++"
	date
	echo "++++++++++++++++++++"

	check_n_backup_previous_installation
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	deploy_current_installation
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	create_launcher
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	echo "Installation successful"
}

check_identity(){
	MY_IDENTITY=$(whoami)
	if [ ${MY_IDENTITY} != "root" ]; then
		echo "This installer needs root permission to run."
		return 1
	fi
}

main(){

	# Check whether root
	check_identity
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	# Creates folder for installation log file
	mkdir -p ${LOGFILE_DIR}
	Z_SUCCESS=${PIPESTATUS}
	if [ ${Z_SUCCESS} != 0 ]; then return ${Z_SUCCESS}; fi

	# Performs installation
	do_installation 2>&1 | tee -a $LOGFILE
}

main
