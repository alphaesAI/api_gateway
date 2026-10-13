from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class CDSServiceDefinition(BaseModel):
    id: str
    hook: str
    title: str
    description: str

class CDSRequest(BaseModel):
    hook: str
    hookInstance: str
    context: Dict[str, Any]
    prefetch: Optional[Dict[str, Any]] = None

class CDSFeedback(BaseModel):
    hookInstance: str
    outcome: Optional[str] = None
    acceptedSuggestions: Optional[List[str]] = None
    feedback: Optional[Dict[str, Any]] = None