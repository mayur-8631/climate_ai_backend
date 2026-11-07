from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class StakeholderType(str, Enum):
    ALL = "all"
    MUNICIPAL = "municipal"
    CITIZENS = "citizens"
    DISASTER_MANAGEMENT = "disaster_management"
    AGRICULTURE = "agriculture"


class UrgencyLevel(str, Enum):
    CRITICAL = "Critical"
    WARNING = "Warning"
    ADVISORY = "Advisory"
    INFO = "Info"


class RecommendationItem(BaseModel):
    id: str
    stakeholder: StakeholderType
    urgency: UrgencyLevel
    title: str
    description: str
    action_type: str
    primary_hazard: str
    estimated_impact: str


class RecommendationsResponse(BaseModel):
    location: str
    risk_level: str
    climate_risk_score: int
    stakeholder_filter: StakeholderType
    total_recommendations: int
    recommendations: List[RecommendationItem]

