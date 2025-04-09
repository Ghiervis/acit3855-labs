import connexion
from flask_cors import CORS
import requests
import json
import logging
import logging.config
import yaml
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os

# Load config
with open("config/app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f)

with open("config/log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger("basicLogger")
DATA_FILE = app_config["datastore"]["filename"]

def fetch(url):
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            logger.error(f"Failed to fetch from {url}: {res.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exception fetching from {url}: {e}")
        return None

def check_consistency():
    logger.info("Running consistency check...")

    stats_proc = fetch(app_config["stats"]["processing_url"])
    stats_anlz = fetch(app_config["stats"]["analyzer_url"])

    analyzer_base_url = app_config["stats"]["analyzer_url"].rsplit('/stats', 1)[0]
    analyzer_url_pp = f"{analyzer_base_url}/events/player-performance?index=0"
    analyzer_url_ai = f"{analyzer_base_url}/events/audience-interaction?index=0"

    pp_event = fetch(analyzer_url_pp)
    ai_event = fetch(analyzer_url_ai)

    if not all([stats_proc, stats_anlz, pp_event, ai_event]):
        logger.error("One or more sources failed. Skipping check.")
        return

    inconsistencies = []
    if stats_proc["num_player_performance"] != stats_anlz["num_player_performance"]:
        inconsistencies.append("Player performance count mismatch.")
    if stats_proc["num_audience_interaction"] != stats_anlz["num_audience_interaction"]:
        inconsistencies.append("Audience interaction count mismatch.")

    result = {
        "timestamp": datetime.now().isoformat(),
        "processing_stats": stats_proc,
        "analyzer_stats": stats_anlz,
        "pp_event": pp_event,
        "ai_event": ai_event,
        "inconsistencies": inconsistencies
    }

    with open(DATA_FILE, "w") as f:
        json.dump(result, f, indent=2)

    logger.info("Check complete.")

def get_checks():
    if not os.path.exists(DATA_FILE):
        return {"message": "No check results found."}, 404
    with open(DATA_FILE, "r") as f:
        return json.load(f), 200

def get_update():
    check_consistency()
    return {"message": "Check performed."}, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(check_consistency, "interval", seconds=app_config["scheduler"]["period_sec"])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("consistency_check.yaml", strict_validation=True, validate_responses=True)
CORS(app.app)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8200, host="0.0.0.0")
