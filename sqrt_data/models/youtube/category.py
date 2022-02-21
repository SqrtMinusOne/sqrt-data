# [[file:../../../org/youtube.org::*Category][Category:1]]
import sqlalchemy as sa
from sqrt_data.models import Base

__all__ = ['Category']


class Category(Base):
    __table_args__ = {'schema': 'youtube'}
    __tablename__ = 'category'

    id = sa.Column(sa.Integer(), primary_key=True)
    name = sa.Column(sa.Text(), nullable=False)
# Category:1 ends here
