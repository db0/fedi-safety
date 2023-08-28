from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from loguru import logger

# Create an SQLite in-memory database for demonstration purposes
engine = create_engine('sqlite:///lemmy_safety.db')

Base = declarative_base()

class CheckedImage(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False, unique=True)
    nsfw = Column(Boolean, default=None)
    csam = Column(Boolean, default=None)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)


# Create the tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
db = Session()

def is_image_checked(key):
    return db.query(CheckedImage).filter_by(filename=key).first()

def is_image_csam(key):
    return db.query(CheckedImage).filter_by(filename=key).first().csam

def is_image_nsfw(key):
    return db.query(CheckedImage).filter_by(filename=key).first().nsfw

def record_image(key, csam=False, nsfw=None):
    image: CheckedImage = db.query(CheckedImage).filter_by(filename=key).first()
    if not image:
        new_image = CheckedImage(
            filename=key, 
            csam=csam,
            nsfw=nsfw,
        )
        db.add(new_image)
        logger.debug(f"Recorded {key} in the DB as csam:{csam} and nsfw:{nsfw}")
    else:
        image.csam = csam
        image.nsfw = nsfw
        logger.debug(f"Updated {key} in the DB as csam:{csam} and nsfw:{nsfw}")
    db.commit()
        