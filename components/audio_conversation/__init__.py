import os
import streamlit.components.v1 as components
from typing import Optional, Dict, Any
import json

# Get the directory of this file
_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTEND_DIR = os.path.join(_COMPONENT_DIR, "frontend")

# Declare the component
_audio_conversation_component = components.declare_component(
    "audio_conversation",
    path=_FRONTEND_DIR,
)

def audio_conversation(
    instructions: str,
    api_key: str,
    conversation_id: Optional[str] = None,
    user_identifier: Optional[str] = None,
    key: Optional[str] = None,
    height: int = 1000
) -> Optional[Dict[str, Any]]:
    """
    Create an audio conversation component for PhysioBot.
    
    Parameters
    ----------
    instructions : str
        The prompt/instructions for the AI conversation partner
    api_key : str
        OpenAI API key for realtime audio
    conversation_id : str, optional
        Unique identifier for this conversation session
    user_identifier : str, optional
        Identifier for the current user
    key : str, optional
        A unique key for this component instance
    height : int, default 1000
        Height of the component in pixels
        
    Returns
    -------
    dict or None
        Dictionary containing conversation data when conversation is completed,
        None otherwise. The dictionary includes:
        - transcript_segments: List of conversation exchanges
        - session_summary: Summary metrics
        - conversation_metrics: Detailed metrics
    """
    
    # Prepare component arguments
    component_args = {
        "instructions": instructions,
        "api_key": api_key,
        "conversation_id": conversation_id or f"conv_{hash(str(instructions))}", 
        "user_identifier": user_identifier or "anonymous",
    }
    
    # Call the component
    component_value = _audio_conversation_component(
        **component_args,
        key=key,
        height=height
    )
    
    # Return the result
    return component_value