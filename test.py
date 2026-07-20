import random
import time
import requests

BASE_URL = "http://127.0.0.1:8000/api/update-reading/"

# Existing ParticipentCycle IDs
DEVICE_IDS = [1, 2, 3, 4]


while True:

    for device in DEVICE_IDS:

        voltage = round(random.uniform(220, 240), 2)

        amperage = round(random.uniform(1, 15), 2)

        power = round(voltage * amperage, 2)

        payload = {
            "cycle_id": device,
            "voltage": voltage,
            "amperage": amperage,
            "power": power,
        }

        try:
            response = requests.post(
                BASE_URL,
                json=payload,
                timeout=5,
            )

            print(response.json())

        except Exception as e:
            print(e)

    time.sleep(2)