# [[file:../../../org/telegram.org::*Deploy][Deploy:1]]
from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule

from sqrt_data_service.api import settings
from .telegram import telegram_load

def create_deploy():
    deployment = Deployment.build_from_flow(
        flow=telegram_load,
        name="telegram_load",
        work_queue_name=settings.prefect.queue,
        parameters={"directory": '/home/pavel/logs-not-sync/telegram.json'}
    )
    deployment.apply()

if __name__ == '__main__':
    create_deploy()
# Deploy:1 ends here
