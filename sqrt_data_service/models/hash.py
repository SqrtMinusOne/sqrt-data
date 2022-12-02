# [[file:../../org/core-new.org::*Hashes][Hashes:1]]
import sqlalchemy as sa
from sqrt_data_service.models import Base

__all__ = ['FileHash']


class FileHash(Base):
    __table_args__ = {'schema': 'hashes'}
    __tablename__ = 'file_hash'

    file_name = sa.Column(
        sa.String(1024),
        primary_key=True,
    )
    hash = sa.Column(sa.String(256), nullable=False)
# Hashes:1 ends here
