from pydantic import BaseModel
from typing import List, Optional

class PromptRequest(BaseModel):
    prompt: str

class StoryGenerationRequest(BaseModel):
    theme: str
    age_group: str
    educational_value: str
    setting: str
    characters: List[str]

class StoryGenerationResponse(BaseModel):
    story_markdown: Optional[str] = None
    issues: List[str] = []
    