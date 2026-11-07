from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app.schemas.common import Coordinates

router = APIRouter()


class WardInfo(BaseModel):
    name: str
    ward_code: str
    coordinates: Coordinates
    elevation_m: float
    description: str


class LocationDetail(BaseModel):
    city: str
    state: str
    country: str
    coordinates: Coordinates
    wards: List[WardInfo]


PUNE_LOCATION = LocationDetail(
    city="Pune",
    state="Maharashtra",
    country="India",
    coordinates=Coordinates(latitude=18.5204, longitude=73.8567),
    wards=[
        WardInfo(
            name="Shivajinagar",
            ward_code="PUN-SHV-01",
            coordinates=Coordinates(latitude=18.5314, longitude=73.8446),
            elevation_m=560.0,
            description="Core administrative & transit hub with IMD Pune reference station"
        ),
        WardInfo(
            name="Kothrud",
            ward_code="PUN-KOT-02",
            coordinates=Coordinates(latitude=18.5074, longitude=73.8077),
            elevation_m=575.0,
            description="Dense residential zone along Mutha river foothills"
        ),
        WardInfo(
            name="Hadapsar",
            ward_code="PUN-HAD-03",
            coordinates=Coordinates(latitude=18.5089, longitude=73.9259),
            elevation_m=555.0,
            description="Commercial & industrial corridor with CPCB air monitoring station"
        ),
        WardInfo(
            name="Lohegaon / Viman Nagar",
            ward_code="PUN-LOH-04",
            coordinates=Coordinates(latitude=18.5822, longitude=73.9197),
            elevation_m=580.0,
            description="Airport zone with rapid urban expansion and open thermal exposure"
        ),
        WardInfo(
            name="Hinjawadi",
            ward_code="PUN-HIN-05",
            coordinates=Coordinates(latitude=18.5913, longitude=73.7389),
            elevation_m=590.0,
            description="Major IT hub with high vehicular traffic and impermeable concrete surfaces"
        ),
        WardInfo(
            name="Katraj",
            ward_code="PUN-KAT-06",
            coordinates=Coordinates(latitude=18.4575, longitude=73.8677),
            elevation_m=620.0,
            description="Southern foothill gateway near Katraj lake and ghat bypass"
        )
    ]
)


@router.get("", response_model=List[LocationDetail])
async def list_supported_locations():
    """List all supported pilot locations and micro-ward coordinates."""
    return [PUNE_LOCATION]

