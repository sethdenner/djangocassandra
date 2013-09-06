#!/bin/bash
# =================================================================================#
#     Setup script that takes care of installing all of the Knotis dependencines
#     and configuring the environment to run the Knotis platform.
# 
#     Example:
#         setup.sh <env_name> <install_location:default=${DEFAULT_INSTALL_LOCATION}>
# =================================================================================#
# Exit on command failure
set -e
export setup_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Generate log files/directories
date_string=$(date +%Y%m%d%H%M%S%N)
log_dir="./logs/${date_string}"
if [[ ! -d ./logs ]] ; then
    mkdir --mode=-t ./logs
fi
if [[ ! -d ${log_dir} ]] ; then
    mkdir --mode=-t ${log_dir}
fi
error_log=${log_dir}/error.log
output_log=${log_dir}/output.log
touch ${output_log} ${error_log} 

# Create temporary directory
if [[ ! -d ./tmp ]] ; then
    mkdir --mode=-t ./tmp ; else
    chmod -t ./tmp
fi
export tmp=$(readlink -e ./tmp)

(
config_file=${1}
if [[ ! -e ${config_file} ]] ; then
    echo "Setup Error: could not open config file ${config_file}." >&2 ; exit 1 ; else
    . ${config_file}
fi 

# Create knotis user and group on the system
id -g ${ADMIN_GROUP} > /dev/null 2>&1 || groupadd --system ${ADMIN_GROUP}
id -u ${ADMIN_USER} > /dev/null 2>&1 || useradd --system -N ${ADMIN_USER}
chsh -s /bin/bash ${ADMIN_USER}
usermod -a -G ${ADMIN_GROUP} ${ADMIN_USER}

if [[ ${2} ]] ; then
    export install_location=${2} ; else
    echo "No install location provided. using default: ${DEFAULT_INSTALL_LOCATION}"
    export install_location=${DEFAULT_INSTALL_LOCATION}
fi

mkdir -p ${install_location} ${install_location}/logs ${install_location}/run/eggs || { echo "Failed to create install location at: ${install_location}" >&2 ; exit 1 ; }

chown -R ${ADMIN_USER}:${ADMIN_GROUP} ${install_location}
chmod -R 760 ${install_location}
usermod -m -d ${install_location} ${ADMIN_USER}

echo "Running install scripts:"
installers_dir="$(pwd)/installers"
for file in ${INSTALLERS[@]} ; do
    installer="${installers_dir}/${file}"
    if [[ ! -f ${installer} ]] ; then
	echo -e "Could not find installer named ${file}. Skipping!" >&2 ; continue
    fi
    echo -e "Running ${installer}..." >> ${output_log}
    ${installer} || { echo "Install script ${installer} failed. Aborting setup." >&2 ; exit 1 ; }
done

rm -rf ${tmp}

) >> ${output_log} 2>> ${error_log}