from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

class PromptRequest(BaseModel):
    prompt: str
    
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UpdateProfileRequest(BaseModel):
    username: str
    email: str
    institution: Optional[str] = None
    bio: Optional[str] = None

class StoryGenerationRequest(BaseModel):
    theme: str
    age_group: str
    educational_value: str
    setting: str
    characters: List[str]
    title: Optional[str] = None
    creator_id: Optional[Union[str, int]] = None

class StoryGenerationResponse(BaseModel):
    story_markdown: Optional[str] = None
    issues: List[str] = Field(default_factory=list)
    story_id: Optional[str] = None

class StorySaveRequest(BaseModel):
    creator_id: str
    title: str
    contents: str

class StoryUpdateRequest(BaseModel):
    title: Optional[str] = None
    contents: Optional[str] = None


class StoryListItem(BaseModel):
    id: str
    creator_id: str
    title: str
    contents: str
    created_at: datetime


class StoryDetailResponse(BaseModel):
    id: str
    creator_id: str
    title: str
    contents: str
    created_at: datetime


class StoryStatsResponse(BaseModel):
    created_count: int
    reads_count: int
    saved_count: int
