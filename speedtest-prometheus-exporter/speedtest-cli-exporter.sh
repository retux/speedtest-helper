#!/usr/bin/env bash

# Parses speedtest-cli output and writes it to .prom files
PROM_TXT_COLLECTOR_DIR=/var/run/shm/prometheus-text-collector
SPEEDTEST_CLI_PATH=/usr/local/bin/speedtest-cli

function validate_parameters {
    if [[ $# -lt 1 ]];then
        usage
        exit 0
    fi
   if [[ -n ${2} ]]; then
        PROM_TXT_COLLECTOR_DIR=${2}
    fi
    PROM_TXT_COLLECTOR_FILE=${PROM_TXT_COLLECTOR_DIR}/speedtest-cli.prom
    PROM_TXT_COLLECTOR_FILE_TMP=${PROM_TXT_COLLECTOR_DIR}/speedtest-cli.prom.tmp
    ENV=${1}
    mkdir -p ${PROM_TXT_COLLECTOR_DIR} 
    if [[ ! -d ${PROM_TXT_COLLECTOR_DIR} ]];then
        echo "[error] directory ${PROM_TXT_COLLECTOR_DIR} does not exist. Exiting."
        exit 0
    fi
 
}

function usage {
    echo "Usage ${0} <env> <metrics_path>"
    echo "<env> name helps to identify metrics."
    echo "<metrics_path> is the location where files will be written, must match with node exporter's "
    exit 0
}

function detect_speedtest-cli {
    speedtest_test_cli=`which speedtest-cli`
    if [[ ! -f ${speedtest_test_cli} ]]; then
        echo "[warn] speedtest-cli is not in PATH, try alternative location:"
        speedtest_bin_path=${SPEEDTEST_CLI_PATH}
        if [[ ! -f ${SPEEDTEST_CLI_PATH} ]]; then
            echo "[Error] speedtest-cli binary was not found. Exit."
        fi 
    fi
    speedtest_bin_path=${speedtest_test_cli}
}

function read_speedtest-cli {
    COMMAND=${speedtest_bin_path}
    #COMMAND="cat /var/tmp/speedtest-cli.log"
    rm -f ${PROM_TXT_COLLECTOR_FILE_TMP}
    $COMMAND | while read line
    do
        if [[ "${line}" =~ [0-9]*ms$ ]]; then
            latency=`echo ${line} | egrep -o "([0-9])*\.[0-9]* ms$" | sed  -e 's/ms//g' | tr -d '[:space:]'` 
            echo "speedtest_cli{name=\"latency\", category=\"bandwidth\", environment=\"${ENV}\"} ${latency}" >> ${PROM_TXT_COLLECTOR_FILE_TMP}
        fi
        if [[ "${line}" =~ Download: ]]; then
            download_rate=`echo ${line} | cut -d: -f2 | sed -e 's/Mbits\/s//g' | tr -d '[:space:]'` 
            echo "speedtest_cli{name=\"download\", category=\"bandwidth\", environment=\"${ENV}\"} ${download_rate}" >> ${PROM_TXT_COLLECTOR_FILE_TMP}
        fi
        if [[ "${line}" =~ Upload: ]]; then
            upload_rate=`echo ${line} | cut -d: -f2 | sed -e 's/Mbits\/s//g' | tr -d '[:space:]'` 
            echo "speedtest_cli{name=\"upload\", category=\"bandwidth\", environment=\"${ENV}\"} ${upload_rate}" >> ${PROM_TXT_COLLECTOR_FILE_TMP}
        fi
    done
    cp  ${PROM_TXT_COLLECTOR_FILE_TMP} ${PROM_TXT_COLLECTOR_FILE}
    rm -f ${PROM_TXT_COLLECTOR_FILE_TMP}
}



function main {
    validate_parameters $*
    detect_speedtest-cli
    read_speedtest-cli

}

main $*
