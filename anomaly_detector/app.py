import logging.config
import connexion
from flask_cors import CORS
import yaml
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from datetime import datetime
import os

with open("config/app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f)

with open("config/log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")

DATA_FILE = app_config["datastore"]["filename"]

def get_kafka_messages():
    kafka_host = f"{app_config['kafka']['hostname']}:{app_config['kafka']['port']}"
    client = KafkaClient(hosts=kafka_host)
    topic = client.topics[app_config["kafka"]["topic"].encode()]
    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True,
        auto_offset_reset=OffsetType.EARLIEST,
        consumer_timeout_ms=1000
    )
    messages = [json.loads(msg.value.decode("utf-8")) for msg in consumer]
    consumer.stop()
    return messages

def is_anomaly(event):
    if event["type"] == "player-performance":
        return event["score"] < 0 or event["score"] > 100
    elif event["type"] == "audience-interaction":
        return event["engagement_level"] < 0 or event["engagement_level"] > 10
    return False

def update_anomalies():
    events = get_kafka_messages()
    anomalies = [e for e in events if is_anomaly(e)]

    result = {
        "timestamp": datetime.now().isoformat(),
        "anomalies": anomalies
    }

    with open(DATA_FILE, "w") as f:
        json.dump(result, f, indent=2)

    logger.info("Anomaly update complete.")
    return {"message": "Anomalies updated"}, 200

def get_anomalies():
    if not os.path.exists(DATA_FILE):
        return {"message": "No anomaly data found"}, 404
    with open(DATA_FILE, "r") as f:
        return json.load(f), 200

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("anomaly.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)

if __name__ == "__main__":
    app.run(port=8210, host="0.0.0.0")
