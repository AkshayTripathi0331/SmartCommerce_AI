from fastapi import APIRouter, status

from app.api.v1.deps import DbSession, CurrentUser
from app.schemas import ChatRequest, ChatResponse, MessageResponse
from app.ai.shopping_agent import ShoppingAgent

router = APIRouter(prefix="/chat", tags=["AI Chat"])


@router.post("", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    db: DbSession,
    current_user: CurrentUser,
):
    """
    Send a message to the AI shopping assistant.
    
    The assistant can:
    - Search for products
    - Add items to your cart
    - Get personalized recommendations
    - Answer policy questions
    - Check order status
    """
    agent = ShoppingAgent(db, current_user.id)
    result = await agent.chat(request.message)
    
    return ChatResponse(
        response=result["response"],
        tool_calls=result.get("tool_calls"),
    )


@router.delete("/history", response_model=MessageResponse)
async def clear_chat_history(
    db: DbSession,
    current_user: CurrentUser,
):
    """Clear conversation history with the AI assistant."""
    agent = ShoppingAgent(db, current_user.id)
    await agent.clear_conversation()
    
    return MessageResponse(message="Conversation history cleared")
