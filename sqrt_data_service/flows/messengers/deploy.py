# [[file:../../../org/messengers.org::*Deploy][Deploy:1]]
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from sqrt_data_service.api import settings
from .telegram import telegram_load
from .aggregate import messengers_aggregate

def create_deploy():
    deployment_1 = Deployment.build_from_flow(
        flow=telegram_load,
        name="telegram_load",
        work_queue_name=settings.prefect.queue,
        parameters={"file_name": '/home/pavel/logs-not-sync/telegram.json'}
    )
    deployment_1.apply()

    deployment_2 = Deployment.build_from_flow(
        flow=messengers_aggregate,
        name="messengers_aggregate",
        work_queue_name=settings.prefect.queue
    )
    deployment_2.apply()

if __name__ == '__main__':
    create_deploy()
# Deploy:1 ends here
