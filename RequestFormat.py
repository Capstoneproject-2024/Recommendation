from pydantic import BaseModel
from datetime import datetime
from typing import List


class ExtractBody(BaseModel):
    review: str

class MatchBody(BaseModel):
    title: str
    review: str
    recommendation_num: int

class QuotBody(BaseModel):
    question_id: str
    user_id: str
    past_data_num: int

