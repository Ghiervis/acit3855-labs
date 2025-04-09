import logging.config
import connexion
import yaml
import json
import httpx
import time   
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone

# Load processing configuration from app_conf.yml
with open("config/app_conf.yml", "r") as f:
    app_config = yaml.safe_load(f)

# Load logging configuration from log_conf.yml
with open("config/log_conf.yml", "r") as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

DATA_FILE = app_config["datastore"]["filename"]

logger = logging.getLogger('basicLogger')

# Use the URLs defined in the config (using Docker's internal DNS)
pp_url = app_config["eventstores"]["player_performance"]["url"]
ai_url = app_config["eventstores"]["audience_interaction"]["url"]

def fetch_with_retries(url, retries=3, delay=2):
    """Fetch a URL with retries if connection fails due to DNS resolution errors."""
    for attempt in range(retries):
        try:
            response = httpx.get(url, timeout=5.0)
            return response
        except httpx.ConnectError as ce:
            logger.error("Connection error fetching %s: %s", url, ce)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None

def get_stats():
    logger.info("Request for stats received")
    try:
        with open(DATA_FILE, "r") as fd:
            stats = json.load(fd)
            logger.debug(stats)
            logger.info("Request for stats completed")
    except Exception as e:
        logger.error("Failed to get statistics: " + str(e))
        return {"message": "Statistics do not exist"}, 404
    return stats, 200

def populate_stats():
    logger.info("Periodic processing started")
    
    # For demonstration purposes, we use a fixed start timestamp.
    start_timestamp = "2025-01-01T00:00:00Z"
    end_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    pp_full_url = f"{pp_url}?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}"
    ai_full_url = f"{ai_url}?start_timestamp={start_timestamp}&end_timestamp={end_timestamp}"

    pp_response = fetch_with_retries(pp_full_url)
    ai_response = fetch_with_retries(ai_full_url)

    num_pp = 0
    num_ai = 0

    if pp_response and pp_response.status_code == 200:
        try:
            events_pp = pp_response.json()
            num_pp = len(events_pp)
        except Exception as e:
            logger.error("Error processing player-performance response: %s", e)
    if ai_response and ai_response.status_code == 200:
        try:
            events_ai = ai_response.json()
            num_ai = len(events_ai)
        except Exception as e:
            logger.error("Error processing audience-interaction response: %s", e)

    stats = {
        "num_player_performance": num_pp,
        "num_audience_interaction": num_ai
    }
    logger.info("Event stats computed: %s", stats)

    # write to data file here
    with open(DATA_FILE, "w") as fd:
        json.dump(stats, fd, indent=4)

    logger.info("Periodic processing ended")

def init_scheduler():
    # Initializes and starts the background scheduler
    time.sleep(5)
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['interval'])
    sched.start()

# Create the Connexion app and add the API specification.
app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("stats.yaml", strict_validation=True, validate_responses=True)

from connexion.middleware import MiddlewarePosition
# from starlette.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     position=MiddlewarePosition.BEFORE_EXCEPTION,
#     allow_origins=["*"],         
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

if __name__ == "__main__":
    init_scheduler()
    # Listen on all interfaces so the container is externally accessible.
    app.run(port=8100, host="0.0.0.0")
