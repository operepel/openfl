#!/bin/bash

# Test the pipeline

TEMPLATE=${1:-'keras_cnn_mnist'}  # ['torch_cnn_mnist', 'keras_cnn_mnist']
FED_WORKSPACE=${2:-'fed_work12345alpha81671'}   # This can be whatever unique directory name you want
COL1=${3:-'one123dragons'}  # This can be any unique label (lowercase)
COL2=${4:-'beta34unicorns'} # This can be any unique label (lowercase)

FQDN=$(hostname --all-fqdns | awk '{print $1}')

create_collaborator() {

    FED_WORKSPACE=$1
    FED_DIRECTORY=$2
    COL=$3
    COL_DIRECTORY=$4

    ARCHIVE_NAME="${FED_WORKSPACE}.zip"

    # Copy workspace to collaborator directories (these can be on different machines)
    rm -rf ${COL_DIRECTORY}    # Remove any existing directory
    mkdir -p ${COL_DIRECTORY}  # Create a new directory for the collaborator
    cd ${COL_DIRECTORY}
    fx workspace import --archive ${FED_DIRECTORY}/${ARCHIVE_NAME} # Import the workspace to this collaborator

    # Create collaborator certificate request
    cd ${COL_DIRECTORY}/${FED_WORKSPACE}
    fx collaborator generate-cert-request -n ${COL} --silent # Remove '--silent' if you run this manually

    # Sign collaborator certificate 
    cd ${FED_DIRECTORY}  # Move back to the Aggregator
    fx collaborator certify --request-pkg ${COL_DIRECTORY}/${FED_WORKSPACE}/col_${COL}_to_agg_cert_request.zip --silent # Remove '--silent' if you run this manually

    #Import the signed certificate from the aggregator
    cd ${COL_DIRECTORY}/${FED_WORKSPACE}
    fx collaborator certify --import ${FED_DIRECTORY}/agg_to_col_${COL}_signed_cert.zip

}

# START
# =====
# Make sure you are in a Python virtual environment with the FL package installed.

# Create FL workspace
rm -rf ${FED_WORKSPACE}
fx workspace create --prefix ${FED_WORKSPACE} --template ${TEMPLATE}
cd ${FED_WORKSPACE}
FED_DIRECTORY=`pwd`  # Get the absolute directory path for the workspace

# Initialize FL plan
fx plan initialize -a ${FQDN}

# Create certificate authority for workspace
fx workspace certify

# Export FL workspace
fx workspace export

# Create aggregator certificate
fx aggregator generate-cert-request --fqdn ${FQDN}

# Sign aggregator certificate
fx aggregator certify --fqdn ${FQDN} --silent # Remove '--silent' if you run this manually

# Create collaborator #1
COL1_DIRECTORY=${FED_DIRECTORY}/${COL1}
create_collaborator ${FED_WORKSPACE} ${FED_DIRECTORY} ${COL1} ${COL1_DIRECTORY}

# Create collaborator #2
COL2_DIRECTORY=${FED_DIRECTORY}/${COL2}
create_collaborator ${FED_WORKSPACE} ${FED_DIRECTORY} ${COL2} ${COL2_DIRECTORY}

# # Run the federation
cd ${FED_DIRECTORY}
fx aggregator start & 
sleep 2 
cd ${COL1_DIRECTORY}/${FED_WORKSPACE}
fx collaborator start -n ${COL1} & 
cd ${COL2_DIRECTORY}/${FED_WORKSPACE}
fx collaborator start -n ${COL2}
rm -rf ${FED_DIRECTORY}
