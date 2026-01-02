"""X-ray report generation"""
from typing import Dict
from langchain.schema import HumanMessage
from app.services.llm_provider import llm_provider
from app.prompts.findings_prompt import XrayFindingsPrompts
from app.utils.logger import logger
from app.config import get_settings

settings = get_settings()

class FindingsGenerator:
    """Generates X-ray reports using appropriate model"""
    
    def __init__(self):
        self.medium = llm_provider.medium
        self.strong = llm_provider.strong
    
    async def generate_findings(
        self,
        image_base64: str,
        image_type: str,
        triage_info: Dict,
        patient_age: int = None,
        clinical_indications: str = None,
    ) -> Dict:
        """
        Generate X-ray findings using appropriate model
        
        Args:
            image_base64: Base64 encoded image
            image_type: "chest", "limb", etc.
            triage_info: Triage assessment from TriageEngine
        
        Returns:
            {
                "report": str (full formatted report),
                "model_used": "haiku" | "sonnet",
                "cost": float,
                "triage_info": dict
            }
        """
        try:
            # Decide which model to use
            model, model_name = self._select_model(triage_info)
            
            # Get prompt
            xray_prompts = XrayFindingsPrompts(patient_age, clinical_indications, triage_info=triage_info)
            
            
            prompts = xray_prompts.get_findings_prompt(
            image_type=image_type
            )

            system = prompts["system"]
            user = prompts["user"]
            print(f"system prompt: {system}  \n\nuser prompt: {user}  \n\nimage_type: {image_type}  \n\ntriage_info: {triage_info}")
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": system
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
                            "text": user
                        }
                    ]
                }
            ]
            
            # Generate report
            response = await model.ainvoke(messages)
            
            # Calculate cost
            cost = self._calculate_cost(model_name, response)
            
            logger.info(f"Report generated using {model_name}, cost: ${cost:.4f}")
            
            return {
                "findings": response.content,
                "model_used": model_name,
                "cost": cost,
                "triage_info": triage_info
            }
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            raise
    
    def _select_model(self, triage_info: Dict) -> tuple:
        """Select appropriate model based on triage"""
        
        confidence = triage_info.get("confidence", 0)
        complexity = triage_info.get("complexity", "complex")
        urgency = triage_info.get("urgency", "urgent")
        
        # Use Haiku for simple, high-confidence cases
        if (confidence >= settings.confidence_threshold and 
            complexity == "simple" and 
            urgency == "normal"):
            logger.info("Using Haiku for routine case")
            return self.medium, "haiku"
        
        # Use Sonnet for everything else
        logger.info("Using Sonnet for complex/urgent case")
        return self.strong, "sonnet"
    
    def _calculate_cost(self, model_name: str, response) -> float:
        """Estimate API cost"""
        # Rough estimates based on token usage
        if model_name == "haiku":
            return 0.02
        else:  # sonnet
            return 0.06

# Global instance
findings_generator = FindingsGenerator()