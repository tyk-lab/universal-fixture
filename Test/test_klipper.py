

from time import sleep

from moonrakerpy import MoonrakerPrinter

printer = MoonrakerPrinter("http://192.168.40.129:81/")


#printer.send_gcode("FIRMWARE_RESTART")

sleep(3)

key = "gcode_button "
sensors = printer.list_sensors(key)
dicts = printer.query_sensors(sensors, key)
print(sensors)
print(dicts)
