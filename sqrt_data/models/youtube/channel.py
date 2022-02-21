# [[file:../../../org/youtube.org::*Channel][Channel:1]]
import sqlalchemy as sa
from sqrt_data.models import Base

__all__ = ['Channel']


class Channel(Base):
    __table_args__ = {'schema': 'youtube'}
    __tablename__ = 'channel'

    id = sa.Column(
        sa.String(256),
        primary_key=True,
    )
    name = sa.Column(sa.Text(), nullable=False)
    url = sa.Column(sa.Text(), nullable=False)
    description = sa.Column(sa.Text(), nullable=True)
    country = sa.Column(sa.String(128), nullable=True)
# Channel:1 ends here
