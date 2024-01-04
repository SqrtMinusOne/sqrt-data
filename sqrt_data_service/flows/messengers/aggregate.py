# [[file:../../../org/messengers.org::*Aggregation][Aggregation:1]]
import argparse
import json
import pandas as pd
import sqlalchemy as sa

from sqrt_data_service.api import settings, DBConn
# Aggregation:1 ends here

# [[file:../../../org/messengers.org::*Aggregation][Aggregation:2]]
__all__ = ['messengers_aggregate']
# Aggregation:2 ends here

# [[file:../../../org/messengers.org::*Aggregation][Aggregation:3]]
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
# Aggregation:3 ends here

# [[file:../../../org/messengers.org::*Aggregation][Aggregation:5]]
MSG_VIEWS = """
CREATE OR REPLACE VIEW messengers.all_messages AS
(
SELECT target, sender, is_outgoing, date_trunc('day', date)::date date, is_group, 'vk' messenger
FROM vk.messages
UNION ALL
SELECT coalesce(M.vk, T.target)      target,
       coalesce(M2.vk, T.sender)     sender,
       is_outgoing,
       date_trunc('day', date)::date date,
       is_group,
       'telegram'                    messenger
FROM messengers.telegram T
         LEFT JOIN messengers.mapping M ON M.telegram = T.target
         LEFT JOIN messengers.mapping M2 ON M2.telegram = T.sender
    );

CREATE OR REPLACE VIEW messengers.aggregate AS
SELECT target, sender, is_outgoing, is_group, date, messenger, count(*) count
FROM messengers.all_messages
GROUP BY target, sender, is_outgoing, is_group, date, messenger
ORDER BY date DESC;
"""

def create_views():
    with DBConn.get_session() as db:
        db.execute(MSG_VIEWS)
        db.commit()
# Aggregation:5 ends here

# [[file:../../../org/messengers.org::*Aggregation][Aggregation:6]]
def messengers_aggregate():
    DBConn()
    load_mapping()
    create_views()
# Aggregation:6 ends here
