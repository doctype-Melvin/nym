from pydantic import BaseModel, ConfigDict
from typing import Optional

class PendingDocument(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    filepath: str
    content: str
    text: str
    layout_conf_score: float
    status: str

