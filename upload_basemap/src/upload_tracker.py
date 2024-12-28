"""Module for tracking uploaded files."""
import os
import logging
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class UploadRecord(Base):
    __tablename__ = 'upload_records'
    
    file_key = Column(String, primary_key=True)
    uploaded_at = Column(DateTime, nullable=False)
    original_path = Column(String, nullable=False)
    prefix = Column(String, nullable=False)

class UploadTracker:
    def __init__(self, db_url: str = "postgresql://upload_user:upload_pass@localhost:5432/upload_tracker"):
        """Initialize the upload tracker.
        
        Args:
            db_url: Database connection URL
        """
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def is_uploaded(self, file_path: str, prefix: str) -> bool:
        """Check if a file has been uploaded."""
        file_key = f"{prefix}/{os.path.basename(file_path)}"
        with self.Session() as session:
            return session.query(UploadRecord).filter_by(file_key=file_key).first() is not None

    def mark_uploaded(self, file_path: str, prefix: str):
        """Mark a file as uploaded."""
        file_key = f"{prefix}/{os.path.basename(file_path)}"
        with self.Session() as session:
            try:
                record = UploadRecord(
                    file_key=file_key,
                    uploaded_at=datetime.now(),
                    original_path=file_path,
                    prefix=prefix
                )
                session.merge(record)  # merge will update if exists, insert if not
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error marking file as uploaded: {e}")
                raise

    def get_upload_info(self, file_path: str, prefix: str) -> Optional[Dict]:
        """Get upload information for a file."""
        file_key = f"{prefix}/{os.path.basename(file_path)}"
        with self.Session() as session:
            record = session.query(UploadRecord).filter_by(file_key=file_key).first()
            if record:
                return {
                    "uploaded_at": record.uploaded_at.isoformat(),
                    "original_path": record.original_path,
                    "prefix": record.prefix
                }
            return None
