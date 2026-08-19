from fastapi import APIRouter
from pydantic import BaseModel

from .chat_service import chat
from .training_service import generate_training


router = APIRouter(
    prefix="/api/ai",
    tags=["AI"],
)


class ChatRequest(BaseModel):
    message: str


class TrainingRequest(BaseModel):
    topic: str
    level: str = "beginner"
    goal: str | None = None


@router.post("/chat")
def ai_chat(request: ChatRequest):
    return chat(request.message)


@router.post("/training")
def ai_training(request: TrainingRequest):
    return generate_training(
        topic=request.topic,
        level=request.level,
        goal=request.goal,
    )