import minimalmodbus
import serial
import struct
import time
import csv
import os
from datetime import datetime

# ==============================
# CONFIGURATION
# ==============================

PORT = "COM7"          # Change to your COM Port
SLAVE_ID = 1

BAUDRATE = 9600
PARITY = serial.PARITY_NONE
STOPBITS = 1
TIMEOUT = 1

LOGFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EM2M_Log.csv")

MAX_CONSECUTIVE_ERRORS = 10  # warn if comm errors keep happening back-to-back

# ==============================
# MODBUS CONNECTION
# ==============================

meter = minimalmodbus.Instrument(PORT, SLAVE_ID)

meter.serial.baudrate = BAUDRATE
meter.serial.bytesize = 8
meter.serial.parity = PARITY
meter.serial.stopbits = STOPBITS
meter.serial.timeout = TIMEOUT

meter.mode = minimalmodbus.MODE_RTU

# Set True while debugging
meter.debug = True


# ==============================
# FLOAT READER
# ==============================

def read_float(register, functioncode=4):
    """
    Reads a 32-bit float from two consecutive 16-bit registers.
    EM2M uses word-swapped float (CDAB): the two 16-bit words are
    swapped, but each word itself stays big-endian.

    functioncode=4 -> input registers (FC04)
    functioncode=3 -> holding registers (FC03)
    If you get comm errors or garbage values, the first thing to
    check is whether your meter actually expects FC03 instead of FC04
    for these addresses (check the EM2M Modbus map in the datasheet).
    """
    regs = meter.read_registers(register, 2, functioncode=functioncode)

    data = struct.pack(">HH", regs[1], regs[0])

    return struct.unpack(">f", data)[0]


# ==============================
# CREATE CSV
# ==============================

# if not os.path.exists(LOGFILE):
#     with open(LOGFILE, "w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             "Timestamp",
#             "Voltage(V)",
#             "Current(A)",
#             "Power(W)",
#             "PowerFactor",
#             "Frequency(Hz)",
#             "Energy(kWh)"
#         ])


# print("=" * 60)
# print(" SELEC EM2M-1P-C-100A LIVE MONITOR ")
# print("=" * 60)

consecutive_errors = 0

try:
    while True:

        try:
            voltage = read_float(20)
            current = read_float(22)
            power = read_float(14)
            pf = read_float(24)
            frequency = read_float(26)
            energy = read_float(0)

            consecutive_errors = 0  # reset on success

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print("\n--------------------------------------")
            print(timestamp)
            print("--------------------------------------")
            print(f"Voltage     : {voltage:8.2f} V")
            print(f"Current     : {current:8.3f} A")
            print(f"Power       : {power:8.2f} W")
            print(f"PowerFactor : {pf:8.3f}")
            print(f"Frequency   : {frequency:8.2f} Hz")
            print(f"Energy      : {energy:8.3f} kWh")

            with open(LOGFILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp,
                    voltage,
                    current,
                    power,
                    pf,
                    frequency,
                    energy
                ])

        except Exception as e:
            consecutive_errors += 1
            print("Communication Error")
            print(e)

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print(
                    f"\nWARNING: {consecutive_errors} consecutive comm errors. "
                    "Check RS485 wiring, COM port, and slave ID."
                )

        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    try:
        meter.serial.close()
    except Exception:
        pass