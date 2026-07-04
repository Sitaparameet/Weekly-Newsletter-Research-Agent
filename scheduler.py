import schedule
import time

from database import init_db
from research_agent import ResearchAgent
from digest_generator import DigestGenerator
from utils.logger import log


def run_pipeline():
    """
    Full weekly pipeline:
    1. Collect data
    2. Process with LLM
    3. Generate digest
    """

    log("\n🚀 Running weekly AI newsletter pipeline...\n")

    init_db()

    agent = ResearchAgent()
    agent.run()

    digest = DigestGenerator()
    digest.run()

    log("\n✅ Weekly pipeline completed!\n")


def start_scheduler():
    """
    Register and run the weekly pipeline job every Monday at 09:00.
    """

    schedule.every().monday.at("09:00").do(run_pipeline)

    log("⏰ Scheduler started (runs every Monday at 09:00 AM)")

    while True:
        schedule.run_pending()
        time.sleep(60)