#!/bin/bash
# =================================================================================#
#     Setup script that takes care of installing all of the Knotis dependencines
#     and configuring the environment to run the Knotis platform.
# 
#     Example:
#         setup.sh <env_name> <install_location:default=${DEFAULT_INSTALL_LOCATION}>
# =================================================================================#

# Generate log files/directories
date_string=$(date +%Y%m%d%H%M%S%N)
log_dir="./logs/${date_string}"
mkdir -p ${log_dir}
log_dir=$(readlink -f ${log_dir})
export error_log=${log_dir}/error.log
export output_log=${log_dir}/output.log

if [[ ${1} ]] ; then
    export env_name=${1} ; else
    echo 'Setup Error: no environment specified' >> ${error_log}
    exit 1
fi 

export all_dir="$(pwd)/all"
export env_dir="$(pwd)/${env_name}"

config_file="${env_dir}/config.sh"
if [[ -z ${config_file} ]] ; then
    echo "Setup Error: could not open config file ${config_file}." >> ${error_log} ; exit 1 ;
fi

. ${config_file}

if [[ ${2} ]] ; then
    export install_location=${2} ; else
    echo "No install location provided. using default: ${DEFAULT_INSTALL_LOCATION}" >> ${output_log}
    export install_location=${DEFAULT_INSTALL_LOCATION}
fi

mkdir -p ${install_location} || { echo "Failed to create install location at: ${install_location}" >> ${error_log} ; exit 1 ; }

useradd --system --no-create-home --home-dir ${install_location} --user-group ${ADMIN_GROUP}
chsh -s /bin/bash ${ADMIN_USER}
chown -R knotis:knotis ${install_location}

echo "Running install scripts:" >> ${output_log}
for name in ${INSTALLERS[@]} ; do
    if [[ -f "${env_dir}/${name}" ]] ; then
	installer="${env_dir}/${name}"
    elif [[ -f "${all_dir}/${name}" ]] ; then
	installer="${all_dir}/${name}"
    else
	echo -e "Could not find installer named ${name}. Skipping!" >> ${error_log} ; continue
    fi
    echo -e "Running ${installer}..." >> ${output_log}
    ${installer} 1>> ${output_log} 2>> ${error_log} || { echo "Install script ${installer} failed. Aborting setup." >> ${error_log} ; exit 1 ; }
done
