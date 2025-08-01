"""
Data validation models for PV Simulator
"""
from datetime import datetime
from pydantic import BaseModel, field_validator


class MeterReading(BaseModel):
    timestamp: datetime
    meter: float
    
    @field_validator('meter')
    @classmethod
    def validate_meter(cls, v):
        if not 0 <= v <= 20:
            raise ValueError('Meter value must be between 0 and 20 kW')
        return round(v, 2)


class PVData(BaseModel):
    timestamp: datetime
    meter: float
    pv: float
    net: float  # Net power: PV production - meter consumption
    
    @field_validator('pv')
    @classmethod
    def validate_pv(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('PV value must be between 0 and 10 kW')
        return round(v, 2)
    
    @field_validator('net')
    @classmethod
    def validate_net(cls, v):
        if not -20 <= v <= 10:  # Can be negative (consuming from grid) or positive (feeding to grid)
            raise ValueError('Net value must be between -20 and 10 kW')
        return round(v, 2)
