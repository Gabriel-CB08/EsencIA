from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import base64
import io
from PIL import Image

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent: str = "Colorimetry Agent"

def analyze_image_features(image_data: str) -> Dict[str, Any]:
    """Analyze image for colorimetry features (mock implementation)."""
    try:
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        
        # Mock analysis results for demo
        return {
            'skin_tone': 'light_warm',
            'hair_color': 'brown',
            'eye_color': 'brown',
            'undertone': 'warm',
            'season': 'autumn',
            'confidence': 0.85
        }
    except Exception as e:
        return {
            'skin_tone': 'medium',
            'hair_color': 'unknown',
            'eye_color': 'unknown',
            'undertone': 'neutral',
            'season': 'spring',
            'confidence': 0.0,
            'error': str(e)
        }

def get_color_recommendations(features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate color recommendations based on features."""
    season = features.get('season', 'spring')
    
    color_palettes = {
        'spring': [
            {'name': 'Coral Pink', 'hex': '#FF6B6B', 'category': 'lipstick', 'reason': 'Brightens spring complexion'},
            {'name': 'Peach', 'hex': '#FFAB91', 'category': 'blush', 'reason': 'Natural flush for warm undertones'},
            {'name': 'Golden Yellow', 'hex': '#FFD54F', 'category': 'clothing', 'reason': 'Complements warm skin'},
            {'name': 'Mint Green', 'hex': '#81C784', 'category': 'clothing', 'reason': 'Fresh and youthful'},
        ],
        'summer': [
            {'name': 'Rose Pink', 'hex': '#F48FB1', 'category': 'lipstick', 'reason': 'Soft and elegant for cool undertones'},
            {'name': 'Lavender', 'hex': '#CE93D8', 'category': 'eyeshadow', 'reason': 'Enhances cool complexion'},
            {'name': 'Soft Blue', 'hex': '#81D4FA', 'category': 'clothing', 'reason': 'Harmonizes with cool undertones'},
            {'name': 'Dusty Rose', 'hex': '#BCAAA4', 'category': 'clothing', 'reason': 'Sophisticated and flattering'},
        ],
        'autumn': [
            {'name': 'Burnt Orange', 'hex': '#FF8A65', 'category': 'lipstick', 'reason': 'Rich and warm for autumn types'},
            {'name': 'Golden Bronze', 'hex': '#A1887F', 'category': 'eyeshadow', 'reason': 'Enhances warm undertones'},
            {'name': 'Deep Teal', 'hex': '#26A69A', 'category': 'clothing', 'reason': 'Striking contrast for warm skin'},
            {'name': 'Rust Red', 'hex': '#D84315', 'category': 'clothing', 'reason': 'Perfect for autumn palette'},
        ],
        'winter': [
            {'name': 'True Red', 'hex': '#F44336', 'category': 'lipstick', 'reason': 'Bold and striking for winter types'},
            {'name': 'Deep Purple', 'hex': '#7B1FA2', 'category': 'eyeshadow', 'reason': 'Dramatic and elegant'},
            {'name': 'Royal Blue', 'hex': '#1976D2', 'category': 'clothing', 'reason': 'Classic winter color'},
            {'name': 'Emerald Green', 'hex': '#388E3C', 'category': 'clothing', 'reason': 'Rich and sophisticated'},
        ]
    }
    
    return color_palettes.get(season, color_palettes['spring'])

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """Simple chat endpoint for colorimetry analysis."""
    message = req.message.lower()
    
    # Check if message contains image data
    if "data:image" in req.message:
        try:
            # Extract image data
            image_start = req.message.find("data:image")
            image_data = req.message[image_start:]
            
            # Analyze image
            features = analyze_image_features(image_data)
            recommendations = get_color_recommendations(features)
            
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
            
            return ChatResponse(response=response)
            
        except Exception as e:
            return ChatResponse(response=f"I apologize, but I encountered an error analyzing your image: {str(e)}")
    
    # Handle text messages
    if any(word in message for word in ['color', 'analysis', 'colorimetry', 'help']):
        return ChatResponse(
            response="Hello! I'm your personal colorimetry specialist. I analyze images of women aged 18-35 to provide personalized color recommendations. Please upload a clear photo of yourself using the camera icon, and I'll help you discover your perfect colors! 🎨"
        )
    
    return ChatResponse(
        response="Hi! I specialize in color analysis for women aged 18-35. Upload your photo and I'll provide personalized color recommendations! 💄✨"
    )

@app.get("/agents")
async def get_agents():
    """Return available agents."""
    return [{
        "name": "Colorimetry Agent",
        "description": "A professional colorimetry specialist who analyzes images of women aged 18-35 to provide personalized color recommendations.",
        "tools": ["analyze_colorimetry", "colorimetry_analysis"],
        "handoffs": [],
        "input_guardrails": []
    }]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
