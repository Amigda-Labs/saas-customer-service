from pydantic import BaseModel
from datetime import datetime

class SharedContext(BaseModel):
    name: str
    contact_num: str
    start_time: datetime
    end_time: datetime
