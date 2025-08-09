from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import base64
import io
import json

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class MessageResponse(BaseModel):
    content: str
    agent: str

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[Dict[str, Any]]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[Dict[str, Any]]

def analyze_colorimetry(image_data: str) -> str:
    """Analyze image for colorimetry and return recommendations."""
    try:
        # Mock analysis for demo - in production, use real image analysis
        features = {
            'skin_tone': 'light_warm',
            'hair_color': 'brown',
            'eye_color': 'brown',
            'undertone': 'warm',
            'season': 'autumn',
            'confidence': 0.85
        }
        
        # Color recommendations based on autumn season
        recommendations = [
            {'name': 'Burnt Orange', 'hex': '#FF8A65', 'category': 'lipstick', 'reason': 'Rich and warm for autumn types'},
            {'name': 'Golden Bronze', 'hex': '#A1887F', 'category': 'eyeshadow', 'reason': 'Enhances warm undertones'},
            {'name': 'Deep Teal', 'hex': '#26A69A', 'category': 'clothing', 'reason': 'Striking contrast for warm skin'},
            {'name': 'Rust Red', 'hex': '#D84315', 'category': 'clothing', 'reason': 'Perfect for autumn palette'},
        ]
        
        # Format response
        response = "## 🎨 Your Personal Color Analysis\n\n"
        response += "**Your Color Profile:**\n"
        for key, value in features.items():
            if key != 'error':
                response += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        response += "\n**Perfect Colors for You:**\n"
        for color in recommendations:
            response += f"- **{color['name']}** ({color['hex']}) - {color['category']}: {color['reason']}\n"
        
        response += "\n*These recommendations are based on seasonal color analysis principles, specifically tailored for women aged 18-35.*"
        
        return response
        
    except Exception as e:
        return f"I apologize, but I encountered an error analyzing your image: {str(e)}"

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Main chat endpoint for colorimetry analysis."""
    try:
        conversation_id = req.conversation_id or "default"
        message = req.message
        
        # Check if message contains image data
        if "data:image" in message:
            response_content = analyze_colorimetry(message)
        elif any(word in message.lower() for word in ['color', 'analysis', 'colorimetry', 'help', 'hello', 'hi']):
            response_content = "Hello! I'm your personal colorimetry specialist. I analyze images of women aged 18-35 to provide personalized color recommendations. Please upload a clear photo of yourself using the camera icon, and I'll help you discover your perfect colors! 🎨"
        else:
            response_content = "Hi! I specialize in color analysis for women aged 18-35. Upload your photo and I'll provide personalized color recommendations! 💄✨"
        
        return ChatResponse(
            conversation_id=conversation_id,
            current_agent="Colorimetry Agent",
            messages=[
                MessageResponse(content=message, agent="user"),
                MessageResponse(content=response_content, agent="Colorimetry Agent")
            ],
            events=[],
            context={},
            agents=[{
                "name": "Colorimetry Agent",
                "description": "A professional colorimetry specialist who analyzes images of women aged 18-35 to provide personalized color recommendations.",
                "tools": ["analyze_colorimetry"],
                "handoffs": [],
                "input_guardrails": []
            }],
            guardrails=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def get_agents():
    """Return available agents."""
    return [{
        "name": "Colorimetry Agent",
        "description": "A professional colorimetry specialist who analyzes images of women aged 18-35 to provide personalized color recommendations.",
        "tools": ["analyze_colorimetry"],
        "handoffs": [],
        "input_guardrails": []
    }]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
