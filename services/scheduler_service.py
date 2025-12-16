from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

def init_scheduler(app):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except Exception:
        logger.warning("APScheduler not installed; scheduler disabled.")
        return None

    sched = BackgroundScheduler(daemon=True)

    # Example job: run daily workflow every 24h (dev-safe)
    def _job():
        try:
            with app.app_context():
                from services.workflows.daily import run_daily_workflow
                run_daily_workflow()
        except Exception as e:
            logger.exception("scheduler job failed: %s", e)

    sched.add_job(_job, "interval", hours=24, id="daily_reset", replace_existing=True)
    sched.start()
    app.extensions["scheduler"] = sched
    return sched
