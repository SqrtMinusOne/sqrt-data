# [[file:../../../org/aw.org::*Source models][Source models:6]]
import sqlalchemy as sa
from .bucket import Bucket

__all__ = ['AndroidUnlock']

class AndroidUnlock(Bucket):
    __tablename__ = 'android_unlock'
    __table_args__ = {'schema': 'aw'}
# Source models:6 ends here
