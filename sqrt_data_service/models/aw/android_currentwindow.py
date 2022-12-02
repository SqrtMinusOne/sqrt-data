# [[file:../../../org/aw.org::*Source models][Source models:7]]
import sqlalchemy as sa
from .bucket import Bucket

__all__ = ['AndroidCurrentWindow']

class AndroidCurrentWindow(Bucket):
    __tablename__ = 'android_currentwindow'
    __table_args__ = {'schema': 'aw'}

    app = sa.Column(sa.Text(), nullable=False)
    classname = sa.Column(sa.Text(), nullable=False)
    package = sa.Column(sa.Text(), nullable=False)
# Source models:7 ends here
