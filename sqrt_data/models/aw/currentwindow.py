# [[file:../../../org/aw.org::*Source models][Source models:3]]
import sqlalchemy as sa
from .bucket import Bucket

__all__ = ['CurrentWindow']

class CurrentWindow(Bucket):
    __tablename__ = 'currentwindow'
    __table_args__ = {'schema': 'aw'}

    app = sa.Column(sa.Text(), nullable=False)
    title = sa.Column(sa.Text(), nullable=False)
# Source models:3 ends here
