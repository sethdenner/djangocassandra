#!/bin/bash

function quick_install {
    # ===================================#
    #                                    #
    #     download with git, hg, svn     #
    #     or wget ($1) from uri ($2),    # 
    #                                    #
    #     install with python, dpkg      #
    #     or make ($3) with arguments    #
    #     ($4)                           #
    #                                    #
    # ===================================#
    (
    temp_dir=/tmp/qinstall

    rm -rf "${temp_dir}" 2> /dev/null
    mkdir -p "${temp_dir}"
    cd ${temp_dir}

    echo "downloading from ${2} using ${1} ..."
    if [[ "${1}" =~ .*git$ || "${1}" =~ .*hg$ ]] ; then
        echo "cloning into ${temp_dir} ..."
        "${1}" clone "${2}" "${temp_dir}"

    elif [[ "${1}" =~ .*svn$ || "${1}" =~ .*subversion$ ]] ; then
        "${1}" co "${2}" "${temp_dir}"

    elif [[ "${1}" =~ .*wget$ ]] ; then
        "${1}" "${2}" -P "${temp_dir}"

    else
        echo "BAD BIN: downloader not supported"
        return 1

    fi

    # extract if necessary
    output=$(find "${temp_dir}" -name *.zip)
    for archive in ${output} ; do
        unzip "${archive}" -d "${temp_dir}"

    done

    output=$(find "${temp_dir}" -name *.tar*)
    for archive in ${output} ; do
        tar xvf "${archive}" -C "${temp_dir}"

    done
    
    if [[ "${3}" =~ .*python$ ]] ; then
        echo "installing with python ..."
        output=$(find "${temp_dir}" -name setup.py)
        for setup in "${output}" ; do
        (
            echo "found ${setup} installing ..."
            cd ${setup%/*}
            "${3}" "${setup##*/}" install ${4}
        )
        done
    
    elif [[ "${3}" =~ .*make$ ]] ; then 
        bootstrap_script=$(find "${temp_dir}" -maxdepth 2 -name bootstrap.sh)
        if [[ ${bootstrap_script} ]] ; then
        (
            cd ${bootstrap_script%/*}
            ./${bootstrap_script##*/}
            
        )
        fi
        configure_script=$(find "${temp_dir}" -maxdepth 2 -name configure)
        if [[ ${configure_script} ]] ; then
        (
            cd ${configure_script%/*}
            ./${configure_script##*/}
            "${3}"
            "${3}" install ${4}

        )
        fi

    elif [[ "${3}" =~ .*dpkg$ ]] ; then
        output=$(find "${temp_dir}" -name *.deb)
        for package in ${output} ; do
            "${3}" -i "${package}" ${4} 

        done

    else
        echo "BAD BIN: installer bin not supported"
        return 2

    fi 

    rm -rf "${temp_dir}"
    
    return 0

    )
}
