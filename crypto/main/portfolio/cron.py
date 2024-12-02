from django_cron import CronJobBase, Schedule
from .tasks import record_portfolio_value


class RecordPortfolioValueCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']  # Каждый день в полночь

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'app.record_portfolio_value'

    def do(self):
        record_portfolio_value()
