from typing import TypedDict, List, Optional
from models import StoryGenerationRequest


class StoryState(TypedDict):
    """Estado compartilhado do pipeline LangGraph para geração de histórias."""
    input: StoryGenerationRequest
    draft_story: Optional[str]
    safety_ok: bool
    requirements_ok: bool
    final_story: Optional[str]
    issues: List[str]
