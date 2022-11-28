# [[file:../../../org/aw.org::*Source models][Source models:5]]
import sqlalchemy as sa
from .bucket import Bucket

__all__ = ['WebTab']

class WebTab(Bucket):
    __tablename__ = 'webtab'
    __table_args__ = {'schema': 'aw'}

    url = sa.Column(sa.Text(), nullable=False)
    site = sa.Column(sa.Text(), nullable=False)
    url_no_params = sa.Column(sa.Text(), nullable=False)
    title = sa.Column(sa.Text(), nullable=False)
    audible = sa.Column(sa.Boolean(), nullable=False)
    incognito = sa.Column(sa.Boolean(), nullable=False)
    tab_count = sa.Column(sa.Integer(), nullable=True)
# Source models:5 ends here
