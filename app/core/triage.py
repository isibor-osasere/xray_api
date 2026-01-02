"""X-ray triage logic"""
import json
from typing import Dict
from langchain.schema import HumanMessage
from app.services.llm_provider import llm_provider
from app.prompts.triage_prompt import get_triage_prompt
from app.utils.logger import logger

class TriageEngine:
    """Handles rapid X-ray triage"""
    
    def __init__(self):
        self.llm = llm_provider.medium
    
    async def triage_xray(
        self, 
        image_base64: str,
        image_type: str = "chest"
    ) -> Dict:
        """
        Perform rapid triage of X-ray
        
        Returns:
            {
                "urgency": "urgent" | "routine" | "normal",
                "complexity": "simple" | "complex",
                "confidence": float,
                "preliminary_findings": list,
                "reasoning": str,
                "cost": float
            }
        """
        try:
            prompt = get_triage_prompt(image_type)
            
            messages = [
                {
                    "role": "system",
                    "content": prompt["system"]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt["user"]
                        }
                    ]
                }
            ]
            
            # Call Haiku for fast triage
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            result = self._parse_triage_response(response.content)
            result["cost"] = 0.01  # Approximate cost for triage
            
            logger.info(f"Triage completed: {result['urgency']} / {result['complexity']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Triage error: {e}")
            # Safe fallback: mark as complex/urgent
            return {
                "urgency": "urgent",
                "complexity": "complex",
                "confidence": 0.0,
                "preliminary_findings": ["Error during triage"],
                "reasoning": f"Error: {str(e)}",
                "cost": 0.01,
                "quality_issues": "Unknown",
                "recommended_action": "immediate radiologist review"
            }

                    
    
    def _parse_triage_response(self, response: str) -> Dict:
        """Parse LLM response into structured triage data"""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str.strip())
            
        except Exception as e:
            logger.warning(f"Failed to parse triage JSON: {e}")
            # Return conservative fallback
            return {
                "urgency": "urgent",
                "complexity": "complex",
                "confidence": 0.3,
                "preliminary_findings": ["Could not parse triage"],
                "reasoning": "Defaulting to safe triage",
                "cost": 0.01,
                "quality_issues": "Unknown",
                "recommended_action": "immediate radiologist review"
            }

# Global instance
triage_engine = TriageEngine()