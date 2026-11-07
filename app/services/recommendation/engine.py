from typing import List, Optional
import uuid
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationsResponse,
    StakeholderType,
    UrgencyLevel
)
from app.schemas.risk_score import RiskScoreResponse


class RecommendationEngine:
    """Generates stakeholder-specific climate adaptation recommendations."""

    @classmethod
    def generate_recommendations(
        cls,
        risk: RiskScoreResponse,
        stakeholder_filter: StakeholderType = StakeholderType.ALL
    ) -> RecommendationsResponse:
        items: List[RecommendationItem] = []

        # 1. Heat Hazard Recommendations
        if risk.risks.heat >= 70.0:
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.MUNICIPAL,
                urgency=UrgencyLevel.CRITICAL,
                title="Activate Municipal Heat Action Plan (HAP)",
                description="Deploy misting stations in high-density markets (e.g. Laxmi Road, Mandai), extend cooling shelters, and reschedule outdoor municipal labor to early morning hours.",
                action_type="Emergency Urban Cooling",
                primary_hazard="Heat",
                estimated_impact="Reduces heatstroke emergency hospital admissions by ~35%"
            ))
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.CITIZENS,
                urgency=UrgencyLevel.WARNING,
                title="Hydration & Peak Sun Avoidance Alert",
                description="Avoid direct solar exposure between 12:00 PM and 4:00 PM. High-risk groups (children and elderly) should stay in ventilated or cooled indoor zones.",
                action_type="Public Health Advisory",
                primary_hazard="Heat",
                estimated_impact="Minimizes individual dehydration and heat exhaustion incidents"
            ))
        elif risk.risks.heat >= 45.0:
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.MUNICIPAL,
                urgency=UrgencyLevel.ADVISORY,
                title="Inspect Urban Green Shading & Tree Canopies",
                description="Ensure public park fountains are operational and inspect roadside shade tree health to combat localized urban heat island spots.",
                action_type="Urban Forestry Maintenance",
                primary_hazard="Heat",
                estimated_impact="Buffers microclimate ambient temperature by 1.5°C to 2.5°C"
            ))

        # 2. Flood Hazard Recommendations
        if risk.risks.flood >= 65.0:
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.DISASTER_MANAGEMENT,
                urgency=UrgencyLevel.CRITICAL,
                title="Pre-position Quick Response Flood Teams at Mula-Mutha Basins",
                description="Station de-watering pumps and NDRF/SDRF alert units along Sinhagad Road, Yerawada, and low-lying bridge corridors. Coordinate Khadakwasla dam discharge alerts.",
                action_type="Emergency Flood Response",
                primary_hazard="Flood",
                estimated_impact="Prevents road submergence entrapment and accelerates water clearance"
            ))
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.MUNICIPAL,
                urgency=UrgencyLevel.WARNING,
                title="Clear Stormwater Drain Bottlenecks",
                description="Desilt blocked culverts and storm drains in chronically waterlogged choke points (Pulachiwadi, Deccan, Hadapsar underpasses).",
                action_type="Infrastructure Desilting",
                primary_hazard="Flood",
                estimated_impact="Restores stormwater runoff throughput by up to 60%"
            ))
        elif risk.risks.flood >= 40.0:
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.CITIZENS,
                urgency=UrgencyLevel.ADVISORY,
                title="Monitor Local Weather Alerts Before Commuting",
                description="Check PMC traffic and waterlogging updates before driving through low-elevation subway routes and river bridges.",
                action_type="Commuter Advisory",
                primary_hazard="Flood",
                estimated_impact="Reduces vehicle stall incidents during sudden cloudbursts"
            ))

        # 3. Air Quality Recommendations
        if risk.risks.air_quality >= 60.0:
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.CITIZENS,
                urgency=UrgencyLevel.WARNING,
                title="N95 Mask Advisory for Sensitive Populations",
                description="High PM2.5 particulate density detected. Asthmatic patients and outdoor joggers should limit strenuous morning activities outdoors.",
                action_type="Respiratory Protection",
                primary_hazard="Air Quality",
                estimated_impact="Decreases acute pulmonary flare-ups and asthma emergencies"
            ))
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.MUNICIPAL,
                urgency=UrgencyLevel.WARNING,
                title="Enforce Construction Dust Suppression & Anti-Smog Guns",
                description="Mandate water sprinklers at active construction sites along Hinjawadi and PCMC arterial roads; enforce ban on open biomass and trash burning.",
                action_type="Dust Emission Control",
                primary_hazard="Air Quality",
                estimated_impact="Suppresses local PM10 emissions by up to 25%"
            ))

        # 4. Water Stress Recommendations
        if risk.risks.water_stress >= 65.0:
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.AGRICULTURE,
                urgency=UrgencyLevel.WARNING,
                title="Transition to Micro-Drip Irrigation Schedules",
                description="Schedule irrigation strictly in evening hours to prevent high daytime evaporation loss. Prioritize drought-hardy mulch layers for soil moisture retention.",
                action_type="Agricultural Water Conservation",
                primary_hazard="Water Stress",
                estimated_impact="Conserves ~30% agricultural water usage without crop yield drop"
            ))
            items.append(RecommendationItem(
                id=str(uuid.uuid4())[:8],
                stakeholder=StakeholderType.MUNICIPAL,
                urgency=UrgencyLevel.ADVISORY,
                title="Implement Rotational Water Pressure Management",
                description="Optimize Khadakwasla distribution network pressure to detect main pipeline leaks and maintain equitable reservoir reserve buffers.",
                action_type="Municipal Supply Optimization",
                primary_hazard="Water Stress",
                estimated_impact="Saves up to 15 MLD in unaccounted network transmission losses"
            ))

        # Filter by stakeholder if requested
        if stakeholder_filter != StakeholderType.ALL:
            items = [item for item in items if item.stakeholder == stakeholder_filter]

        return RecommendationsResponse(
            location=risk.location,
            risk_level=risk.risk_level.value,
            climate_risk_score=risk.climate_risk_score,
            stakeholder_filter=stakeholder_filter,
            total_recommendations=len(items),
            recommendations=items
        )

