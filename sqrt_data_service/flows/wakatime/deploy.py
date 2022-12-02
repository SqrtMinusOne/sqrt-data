# [[file:../../../org/wakatime.org::*Deploy][Deploy:1]]
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from sqrt_data_service.api import settings
from .flow import wakatime

def create_deploy():
    deployment = Deployment.build_from_flow(
        flow=wakatime,
        name="wakatime-dump",
        work_queue_name=settings.prefect.queue,
        schedule=(CronSchedule(cron="0 0 * * *"))
    )
    deployment.apply()

if __name__ == '__main__':
    create_deploy()
# Deploy:1 ends here
