# [[file:../../../org/aw.org::*Deploy][Deploy:1]]
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from sqrt_data_service.api import settings
from .main import aw_process

def create_deploy():
    deployment = Deployment.build_from_flow(
        flow=aw_process,
        name="aw-process",
        work_queue_name=settings.prefect.queue,
        schedule=(CronSchedule(cron="0 3 * * *")),
        parameters={"init": False}
    )
    deployment.apply()

if __name__ == '__main__':
    create_deploy()
# Deploy:1 ends here
