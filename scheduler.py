import schedule
import time
from main import run_agent
from config import load_config


def start():
    config = load_config()
    hours = config.post_schedule_hours

    print(f"Scheduler running — posting every {hours} hour(s). Press Ctrl+C to stop.")

    run_agent()  # Run once immediately on start
    schedule.every(hours).hours.do(run_agent)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start()
