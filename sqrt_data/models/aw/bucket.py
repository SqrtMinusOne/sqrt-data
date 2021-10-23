# [[file:../../../org/aw.org::*Source models][Source models:1]]
import sqlalchemy as sa
from sqrt_data.models import Base

__all__ = ['Bucket']


class Bucket(Base):
    __table_args__ = {'schema': 'aw'}
    __abstract__ = True

    id = sa.Column(
        sa.String(256),
        primary_key=True,
    )
    bucket_id = sa.Column(sa.String(256), nullable=False)
    hostname = sa.Column(sa.String(256), nullable=False)
    location = sa.Column(sa.String(256), nullable=False)
    timestamp = sa.Column(sa.DateTime(), nullable=False)
    duration = sa.Column(sa.Float(), nullable=False)
# Source models:1 ends here
