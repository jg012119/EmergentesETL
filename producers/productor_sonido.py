import csv
import json
import os
import time
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("KAFKA_BROKER")
TOPIC = os.getenv("KAFKA_TOPIC_SONIDO")
SLEEP = float(os.getenv("SLEEP_SECONDS", "1")) 

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5
)

csv_path = os.path.join(os.path.dirname(__file__), "data", "WS302-915M SONIDO.csv")

print(f"📡 Enviando datos del sensor WS302-SONIDO desde: {csv_path}")

with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        payload = {
            "timestamp": row.get("time"),
            "noise": float(row.get("object.noise") or 0),
            "noise_max": float(row.get("object.max") or 0),
            "noise_min": float(row.get("object.min") or 0),
            "battery": float(row.get("object.battery") or 0),
            "device": row.get("devAddr")
        }

        print("🔊 [SONIDO] Enviado:", payload)
        producer.send(TOPIC, payload)
        time.sleep(SLEEP)

producer.flush()
producer.close()
