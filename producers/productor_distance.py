import csv
import json
import os
import time
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("KAFKA_BROKER")
TOPIC = os.getenv("KAFKA_TOPIC_DISTANCIA")
SLEEP = float(os.getenv("SLEEP_SECONDS", "1"))

producer = KafkaProducer(
    bootstrap_servers=BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5
)

csv_path = os.path.join(os.path.dirname(__file__), "data", "EM310-UDL.csv")

print(f"📡 Enviando datos del sensor EM310-UDL desde: {csv_path}")

with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        payload = {
            "timestamp": row.get("time"),
            "distance_mm": float(row.get("object.distance") or 0),
            "temperature": float(row.get("object.temperature") or 0),
            "battery": float(row.get("object.battery") or 0),
            "device": row.get("devAddr")
        }

        print("📏 [DISTANCIA] Enviado:", payload)
        producer.send(TOPIC, payload)
        time.sleep(SLEEP)

producer.flush()
producer.close()
