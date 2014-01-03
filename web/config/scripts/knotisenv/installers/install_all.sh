#!/bin/bash

installer_dir="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
installers=$(find ${installer_dir} -maxdepth 1 -name install_*.sh)
echo ${installers}
for installer in ${installers} ; do
    [[ ${installer} =~ .*install_all.sh$ ]] && continue

    ${installer}
    
    done
