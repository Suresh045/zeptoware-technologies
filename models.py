# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

# THIS is the Base your app.py needs
Base = declarative_base()

class Resume(Base):
    __tablename__ = 'resumes'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1024), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    text_content = Column(Text, nullable=True)
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)

    # embedding stored as JSON string of floats
    embedding_json = Column(Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
        }
