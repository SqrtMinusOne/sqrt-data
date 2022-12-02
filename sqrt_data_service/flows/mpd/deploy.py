# [[file:../../../org/mpd.org::*Deploy][Deploy:1]]
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from sqrt_data_service.api import settings
from .flow import load_mpd

def create_deploy():
    deployment = Deployment.build_from_flow(
        flow=load_mpd,
        name="load-mpd",
        work_queue_name=settings.prefect.queue,
        schedule=(CronSchedule(cron="0 1 * * *"))
    )
    deployment.apply()

if __name__ == '__main__':
    create_deploy()
# Deploy:1 ends here
