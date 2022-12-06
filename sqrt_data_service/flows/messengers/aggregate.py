# [[file:../../../org/messengers.org::*Aggregation][Aggregation:1]]
import argparse
import json
import pandas as pd
import sqlalchemy as sa
from prefect import task, flow, get_run_logger

from sqrt_data_service.api import settings, DBConn
# Aggregation:1 ends here

# [[file:../../../org/messengers.org::*Aggregation][Aggregation:2]]
@task
def load_mapping():
    df = pd.read_csv(settings.messengers.mapping_file)
    with DBConn.get_session() as db:
        exists = DBConn.table_exists('mapping', 'messengers', db)
        if exists:
            db.execute(sa.text('truncate table messengers.mapping'))
        db.commit()

    df.to_sql(
        'mapping', schema='messengers', con=DBConn.engine, if_exists='append'
    )
# Aggregation:2 ends here

# [[file:../../../org/messengers.org::*Aggregation][Aggregation:3]]
@flow
def messengers_aggregate():
    DBConn()
    load_mapping()


if __name__ == '__main__':
    messengers_aggregate()
# Aggregation:3 ends here
