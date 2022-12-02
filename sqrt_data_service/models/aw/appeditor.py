# [[file:../../../org/aw.org::*Source models][Source models:4]]
import sqlalchemy as sa
from .bucket import Bucket

__all__ = ['AppEditor']

class AppEditor(Bucket):
    __tablename__ = 'appeditor'
    __table_args__ = {'schema': 'aw'}

    file = sa.Column(sa.Text(), nullable=False)
    project = sa.Column(sa.Text(), nullable=False)
    language = sa.Column(sa.Text(), nullable=False)
# Source models:4 ends here
