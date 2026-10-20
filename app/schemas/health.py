from pydantic import BaseModel

class HealthCheck:
    status: str 
    application: str 
    environment: str
    