# [[file:../../../org/aw.org::*Source models][Source models:2]]
import sqlalchemy as sa
from .bucket import Bucket

__all__ = ['AfkStatus']

class AfkStatus(Bucket):
    __tablename__ = 'afkstatus'
    __table_args__ = {'schema': 'aw'}

    status = sa.Column(sa.Boolean(), nullable=False)
# Source models:2 ends here
