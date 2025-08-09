from __future__ import annotations as _annotations

from agents.extensions.models.litellm_model import LitellmModel
import os
import base64
import random
from pydantic import BaseModel
import string
from typing import List, Dict, Any
import numpy as np
from PIL import Image
import io

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    function_tool,
    handoff,
    GuardrailFunctionOutput,
    input_guardrail,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# =========================
# CONTEXT
# =========================

class ColorimetryContext(BaseModel):
    """Context for colorimetry analysis."""
    image_data: str | None = None  # Base64 encoded image
    detected_features: Dict[str, Any] | None = None
    color_recommendations: List[Dict[str, Any]] | None = None
    analysis_result: str | None = None

def create_initial_context() -> ColorimetryContext:
    """
    Factory for a new ColorimetryContext.
    """
    return ColorimetryContext()

# =========================
# COLORIMETRY FUNCTIONS
# =========================

def analyze_image_features(image_data: str) -> Dict[str, Any]:
    """
    Analyze image to detect features for colorimetry.
    For demo purposes, this returns mock data.
    In production, this would use proper face detection and analysis.
    """
    try:
        # Decode base64 image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        
        # For demo, return mock analysis results
        # In production, you would use face detection and color analysis
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
    """
    Generate color recommendations based on detected features.
    Tailored for women aged 18-35.
    """
    season = features.get('season', 'spring')
    undertone = features.get('undertone', 'neutral')
    
    # Color palettes based on seasonal color analysis
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
            {'name': 'Rust Red', 'hex': '#D84315', 'category': 'clothing', 'reason': 'Bold and flattering'},
        ],
        'winter': [
            {'name': 'True Red', 'hex': '#F44336', 'category': 'lipstick', 'reason': 'Classic and dramatic for winter types'},
            {'name': 'Navy Blue', 'hex': '#1976D2', 'category': 'eyeshadow', 'reason': 'Deep and sophisticated'},
            {'name': 'Emerald Green', 'hex': '#388E3C', 'category': 'clothing', 'reason': 'Vibrant and striking'},
            {'name': 'Pure White', 'hex': '#FFFFFF', 'category': 'clothing', 'reason': 'Crisp and clean contrast'},
        ]
    }
    
    return color_palettes.get(season, color_palettes['spring'])

# =========================
# TOOLS
# =========================



@function_tool(
    name_override="colorimetry_analysis",
    description_override="Analyze an image for colorimetry and recommend colors for women aged 18-35"
)
async def colorimetry_analysis(image_data: str) -> str:
    """
    Analyze an image for colorimetry and provide color recommendations.
    Specifically designed for women aged 18-35.
    """
    try:
        # Analyze image features (mock for demo)
        features = analyze_image_features(image_data)
        
        # Get color recommendations
        recommendations = get_color_recommendations(features)
        
        # Format response
        response = "## 🎨 Colorimetry Analysis Results\n\n"
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

@function_tool(
    name_override="analyze_colorimetry",
    description_override="Analyze an image for colorimetry and recommend colors for women aged 18-35"
)
async def analyze_colorimetry(
    context: RunContextWrapper[ColorimetryContext], 
    image_data: str
) -> str:
    """
    Analyze an image for colorimetry and provide color recommendations.
    Specifically designed for women aged 18-35.
    
    Args:
        image_data: Base64 encoded image data
        
    Returns:
        str: Colorimetry analysis and recommendations
    """
    try:
        # Store image data in context
        context.context.image_data = image_data
        
        # Analyze image features
        features = analyze_image_features(image_data)
        context.context.detected_features = features
        
        # Get color recommendations
        recommendations = get_color_recommendations(features)
        context.context.color_recommendations = recommendations
        
        # Format response
        response = "## 🎨 Colorimetry Analysis Results\n\n"
        response += "**Your Color Profile:**\n"
        for key, value in features.items():
            if key != 'error':
                response += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        response += "\n**Perfect Colors for You:**\n"
        for color in recommendations:
            response += f"- **{color['name']}** ({color['hex']}) - {color['category']}: {color['reason']}\n"
        
        response += "\n*These recommendations are based on seasonal color analysis principles, specifically tailored for women aged 18-35.*"
        
        context.context.analysis_result = response
        return response
        
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error analyzing your image: {str(e)}"
        context.context.analysis_result = error_msg
        return error_msg

# =========================
# HOOKS
# =========================

# No hooks needed for colorimetry-only system

# GUARDRAILS
# =========================

class RelevanceOutput(BaseModel):
    is_relevant: bool
    reason: str

class JailbreakOutput(BaseModel):
    is_safe: bool
    reason: str

@function_tool
async def relevance_guardrail(user_input: str) -> GuardrailFunctionOutput:
    """Check if the user input is relevant to colorimetry analysis."""
    # Allow colorimetry-related queries and general conversation
    colorimetry_keywords = ['color', 'colorimetry', 'analysis', 'image', 'photo', 'picture', 'hello', 'hi', 'help']
    is_relevant = any(keyword in user_input.lower() for keyword in colorimetry_keywords) or len(user_input.strip()) < 50
    
    return GuardrailFunctionOutput(
        output_info=RelevanceOutput(
            is_relevant=is_relevant,
            reason="Colorimetry or general conversation" if is_relevant else "Not related to colorimetry services"
        ),
        tripwire_triggered=not is_relevant
    )

@function_tool
async def jailbreak_guardrail(user_input: str) -> GuardrailFunctionOutput:
    """Check if the user input contains potential jailbreak attempts."""
    # Simple jailbreak detection - in production, use more sophisticated methods
    jailbreak_patterns = [
        "ignore previous instructions",
        "you are now",
        "forget everything",
        "new instructions",
        "system prompt"
    ]
    
    is_safe = not any(pattern in user_input.lower() for pattern in jailbreak_patterns)
    
    result = JailbreakOutput(
        is_safe=is_safe,
        reason="Safe input" if is_safe else "Potential jailbreak attempt detected"
    )
    
    final = result.final_output_as(JailbreakOutput)
    return GuardrailFunctionOutput(output_info=final, tripwire_triggered=not final.is_safe)

# =========================
# AGENTS
# =========================

colorimetry_agent = Agent[ColorimetryContext](
    name="Colorimetry Agent",
    model=LitellmModel(model="gemini/gemini-2.0-flash-lite", api_key=os.getenv("GEMINI_API_KEY")),
    handoff_description="A professional colorimetry specialist who analyzes images of women aged 18-35 to provide personalized color recommendations.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a professional colorimetry specialist who analyzes images of women aged 18-35 
    to provide personalized color recommendations based on their natural features.
    
    Your expertise includes:
    - Seasonal color analysis (Spring, Summer, Autumn, Winter)
    - Undertone detection (warm, cool, neutral)
    - Color recommendations for makeup, clothing, and accessories
    
    When a user provides an image:
    1. Use the analyze_colorimetry tool to process the image
    2. Provide detailed explanations of why certain colors work
    3. Give practical advice on how to incorporate these colors
    4. Be encouraging and professional
    
    Focus on women aged 18-35 and ensure recommendations are age-appropriate and trendy.
    If the image quality is poor or doesn't show a clear face, politely ask for a better image.
    
    If someone just says hello or asks general questions, be friendly and explain that you specialize in color analysis for women aged 18-35.""",
    tools=[analyze_colorimetry, colorimetry_analysis],
    handoffs=[],
    input_guardrails=[relevance_guardrail, jailbreak_guardrail],
)

# No handoff relationships needed for single-agent system
