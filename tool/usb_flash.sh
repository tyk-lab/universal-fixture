#!/bin/bash

# Check the number of parameters
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <mcu_type> <firmware_path>"
    exit 1
fi

# Get tool execution path
SCRIPT_DIR=$(pwd)/tool

# Get the parameters passed in
MCU_TYPE=$1
FIRMWARE_PATH=$2

# Execute different commands according to mcu type
if [ "$MCU_TYPE" == "stm32" ]; then
    output=$(sudo $SCRIPT_DIR/dfu-util -d ,0483:df11 -R -a 0 -s 0x8000000:leave -D "$FIRMWARE_PATH" 2>&1)
    #echo "flash stm32"
elif [ "$MCU_TYPE" == "rp2040" ]; then
    output=$(sudo $SCRIPT_DIR/rp2040_flash "$FIRMWARE_PATH" 2>&1)
    #echo "flash rp2040"
else
    echo "Unsupported MCU type: $MCU_TYPE"
    exit 1
fi

echo "$output"
exit 0
