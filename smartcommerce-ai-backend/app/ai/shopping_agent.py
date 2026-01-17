"""Conversational shopping agent using Gemini with function calling."""
import json
from typing import Optional, List, Dict, Any
from uuid import UUID
import google.generativeai as genai
from google.generativeai.types import content_types
import redis.asyncio as redis

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.ai.config import ai_settings
from app.ai.tools import AgentTools, TOOL_DEFINITIONS


class ConversationMemory:
    """Redis-backed conversation memory."""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self.max_history = 20  # Max messages to keep
    
    async def get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis
    
    def _key(self, user_id: UUID) -> str:
        return f"chat:history:{user_id}"
    
    async def get_history(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get conversation history for user."""
        r = await self.get_redis()
        data = await r.get(self._key(user_id))
        if data:
            return json.loads(data)
        return []
    
    async def add_message(self, user_id: UUID, role: str, content: str):
        """Add a message to history."""
        history = await self.get_history(user_id)
        history.append({"role": role, "parts": [content]})
        
        # Trim to max history
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        r = await self.get_redis()
        await r.setex(
            self._key(user_id),
            86400 * 7,  # 7 days TTL
            json.dumps(history)
        )
    
    async def add_function_call(self, user_id: UUID, name: str, args: dict, result: dict):
        """Add function call and result to history."""
        history = await self.get_history(user_id)
        
        # Add function call
        history.append({
            "role": "model",
            "parts": [{"function_call": {"name": name, "args": args}}]
        })
        
        # Add function response
        history.append({
            "role": "function",
            "parts": [{"function_response": {"name": name, "response": result}}]
        })
        
        if len(history) > self.max_history:
            history = history[-self.max_history:]
        
        r = await self.get_redis()
        await r.setex(self._key(user_id), 86400 * 7, json.dumps(history))
    
    async def clear_history(self, user_id: UUID):
        """Clear conversation history for user."""
        r = await self.get_redis()
        await r.delete(self._key(user_id))
    
    async def close(self):
        if self._redis:
            await self._redis.close()


class ShoppingAgent:
    """Conversational shopping agent with tool calling."""
    
    SYSTEM_PROMPT = """You are a helpful shopping assistant for SmartCommerce AI, an online store.

Your role is to help customers:
- Find and search for products
- Get product recommendations
- Manage their shopping cart
- Answer questions about shipping, returns, and policies
- Check order status

Guidelines:
- Be friendly, helpful, and concise
- When showing products, include key details like price and rating
- Proactively suggest adding items to cart when appropriate
- If a customer seems undecided, offer recommendations
- For policy questions, use the lookup_policy tool
- Format prices as currency (e.g., $99.99)

Always use the available tools to get accurate, up-to-date information."""

    def __init__(self, db: AsyncSession, user_id: UUID):
        genai.configure(api_key=ai_settings.google_api_key)
        self.db = db
        self.user_id = user_id
        self.tools = AgentTools(db, user_id)
        self.memory = ConversationMemory()
        
        # Convert tool definitions to Gemini format
        self.gemini_tools = self._create_gemini_tools()
        
        # Create model with tools
        self.model = genai.GenerativeModel(
            model_name=ai_settings.chat_model,
            tools=self.gemini_tools,
            system_instruction=self.SYSTEM_PROMPT,
        )
    
    def _create_gemini_tools(self):
        """Convert tool definitions to Gemini function declarations."""
        functions = []
        for tool in TOOL_DEFINITIONS:
            functions.append(genai.protos.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        k: genai.protos.Schema(
                            type=self._get_type(v.get("type", "string")),
                            description=v.get("description", ""),
                        )
                        for k, v in tool.get("parameters", {}).get("properties", {}).items()
                    },
                    required=tool.get("parameters", {}).get("required", []),
                )
            ))
        return [genai.protos.Tool(function_declarations=functions)]
    
    def _get_type(self, type_str: str):
        """Convert type string to Gemini proto type."""
        type_map = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }
        return type_map.get(type_str, genai.protos.Type.STRING)
    
    async def _execute_tool(self, name: str, args: dict) -> dict:
        """Execute a tool and return the result."""
        tool_method = getattr(self.tools, name, None)
        if not tool_method:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            result = await tool_method(**args)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def chat(self, message: str) -> dict:
        """
        Process a user message and return a response.
        
        Args:
            message: User's message
            
        Returns:
            Dict with response and any tool calls made
        """
        import asyncio
        
        # Get conversation history
        history = await self.memory.get_history(self.user_id)
        
        # Add user message to history
        await self.memory.add_message(self.user_id, "user", message)
        
        # Build chat with history
        chat = self.model.start_chat(history=history)
        
        # Send message
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat.send_message(message)
        )
        
        tool_calls = []
        
        # Handle function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]
            
            # Check if it's a function call
            if hasattr(part, 'function_call') and part.function_call.name:
                fc = part.function_call
                args = dict(fc.args) if fc.args else {}
                
                # Execute the tool
                result = await self._execute_tool(fc.name, args)
                tool_calls.append({
                    "name": fc.name,
                    "args": args,
                    "result": result,
                })
                
                # Store function call in memory
                await self.memory.add_function_call(
                    self.user_id, fc.name, args, result
                )
                
                # Send function response back to model
                response = await loop.run_in_executor(
                    None,
                    lambda r=result, n=fc.name: chat.send_message(
                        genai.protos.Content(
                            parts=[genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=n,
                                    response={"result": r}
                                )
                            )]
                        )
                    )
                )
            else:
                # It's a text response, we're done
                break
        
        # Get final text response
        final_text = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                final_text += part.text
        
        # Store assistant response
        await self.memory.add_message(self.user_id, "model", final_text)
        
        return {
            "response": final_text,
            "tool_calls": tool_calls if tool_calls else None,
        }
    
    async def clear_conversation(self):
        """Clear conversation history."""
        await self.memory.clear_history(self.user_id)


# Singleton memory instance
conversation_memory = ConversationMemory()
