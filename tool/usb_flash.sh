#!/bin/bash

# Check the number of parameters
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <mcu_type> <burn_method> <firmware_path>"
    exit 1
fi

# Get tool execution path
SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
# Get the parameters passed in
MCU_TYPE=$1
BURN_METHOD=$2
FIRMWARE_PATH=$3

HAS_EXCEPT=0


########################### related function ############################

err_tip() {
    echo "Unsupported MCU type: $MCU_TYPE"
    exit 1
}

flash_dfu() {
# Execute different commands according to mcu type
if [[ "$MCU_TYPE" == *"stm32"* ]]; then
    echo "flash stm32"
else
    HAS_EXCEPT=1
fi

if [ $HAS_EXCEPT == 1 ]; then
    err_tip
fi

output=$(sudo $SCRIPT_DIR/dfu-util -d ,0483:df11 -R -a 0 -s 0x8000000:leave -D "$FIRMWARE_PATH" 2>&1)
}

#Burning with klipper compiled burning software
flash_mount() {
if [ "$MCU_TYPE" == "rp2040" ]; then
    echo "flash rp2040"
else
    HAS_EXCEPT=1
fi

if [ $HAS_EXCEPT == 1 ]; then
    err_tip
fi

output=$(sudo $SCRIPT_DIR/rp2040_flash "$FIRMWARE_PATH" 2>&1)
}


flash_serial_usb() {
end_args=":i"
burn_args="-carduino  -v -p$MCU_TYPE -cwiring -P/dev/ttyACM0 -b115200 -D -Uflash:w:"

if [ "$MCU_TYPE" == "atmega2560" ]; then
    echo "flash atmega2560"
elif [ "$MCU_TYPE" == "atmega328p" ]; then
    echo "flash atmega328p"
else 
    HAS_EXCEPT=1
fi

if [ $HAS_EXCEPT == 1 ]; then
    err_tip
fi
output=$(sudo avrdude  $burn_args$FIRMWARE_PATH$end_args 2>&1)
}

flash_jlink() {
$SCRIPT_DIR/jlink_flash.sh $FIRMWARE_PATH

if [ "$MCU_TYPE" == "STM32F446ZE" ]; then
    echo "flash STM32F446ZE"
else
    HAS_EXCEPT=1
fi

if [ $HAS_EXCEPT == 1 ]; then
    err_tip
fi
    output=$(sudo JLinkExe -device $MCU_TYPE -if SWD -speed 4000 -autoconnect 1 -CommanderScript download.jlink)
}

flash_stlink() {
    output=$(sudo st-flash write $FIRMWARE_PATH 0x08000000)
}


########################### Burn Mode Jump ############################
if [ "$BURN_METHOD" == "dfu" ]; then
    flash_dfu
elif [ "$BURN_METHOD" == "stlink" ]; then
    flash_stlink
elif [ "$BURN_METHOD" == "jlink" ]; then
    flash_jlink
elif [ "$BURN_METHOD" == "serial_usb" ]; then
    flash_serial_usb
elif [ "$BURN_METHOD" == "mount" ]; then
    flash_mount
fi


echo "$output"
exit 0
