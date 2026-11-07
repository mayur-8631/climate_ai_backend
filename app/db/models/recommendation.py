from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.db.session import Base


class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(100), nullable=False, index=True)
    stakeholder = Column(String(50), nullable=False, index=True)
    urgency = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    action_type = Column(String(100), nullable=False)
    primary_hazard = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

