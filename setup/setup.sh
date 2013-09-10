#!/bin/bash
# =================================================================================#
#     Setup script that takes care of installing all of the Knotis dependencines
#     and configuring the environment to run the Knotis platform.
# 
#     Example:
#         setup.sh <env_name> <install_location:default=/srv/knotis/>
# =================================================================================#

# Generate log files/directories
date_string=$(date +%Y%m%d%H%M%S%N)
log_dir="./setup_logs/setup_${date_string}"
mkdir -p ${log_dir}
log_dir=$(readlink -f ${log_dir})
export error_log=${log_dir}/error.log
export output_log=${log_dir}/output.log
touch  ${error_log} ${output_log}

if [[ ${1} ]] ; then
    export env_name=${1} ; else
    echo 'Setup Error: no environment specified' >> ${error_log}
    exit 1
fi 

default_install_location=/srv/knotis

if [[ ${2} ]] ; then
    export install_location=${2} ; else
    echo "No install location provided. using default: ${default_install_location}" >> ${output_log}
    export install_location=${default_install_location}
fi

apt-get install -y git python-software-properties python-support >> ${output_log} 2>> ${error_log} || { echo 'Failed to install dependencies' >> ${error_log} ; exit 1 ; }

mkdir -p ${install_location} || { echo "Failed to create install location at: ${install_location}" >> ${error_log} ; exit 1 ; }

export all_dir="$(pwd)/all"
export env_dir="$(pwd)/${env_name}"

installers=$(find ${all_dir} -maxdepth 1 -regex ".*/[0-9]+_install_.*.sh")
echo ${installers}
for installer in ${installers} ; do
    ${installer} 1>> ${output_log} 2>> ${error_log} || { echo "Install script ${installer} failed. Aborting." >> ${error_log} ; exit 1 ; }
done

installers=$(find ${env_dir} -maxdepth 1 -regex ".*/[0-9]+_install_.*.sh")
echo ${installers}
for installer in ${installers} ; do
    ${installer} 1>> ${output_log} 2>> ${error_log} || { echo "Install script ${installer} failed. Aborting" >> ${error_log} ; exit 1 ; }
done
