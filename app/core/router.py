"""Main orchestration logic"""
from typing import Dict
from app.core import findings_generator
from app.core.triage import triage_engine
from app.core.findings_generator import findings_generator
from app.core.report_generator import report_engine
from app.utils.logger import logger

class XRayRouter:
    """Orchestrates X-ray analysis pipeline"""
    
    async def analyze_xray(
        self,
        image_base64: str,
        image_type: str = "chest_single",
        patient_age: int = None,
        clinical_indications: str = None,
    ) -> Dict:
        """
        Complete X-ray analysis pipeline
        
        Pipeline:
        1. Triage (Haiku - fast, cheap)
        2. Route to appropriate model
        3. Generate report (Haiku or Sonnet)
        4. Return structured result
        
        Returns:
            {
                "triage": {...},
                "report": str,
                "model_used": str,
                "total_cost": float,
                "processing_time": float
            }
        """
        import time
        start_time = time.time()
        
        try:
            # Step 1: Triage
            logger.info("Step 1: Triaging X-ray...")
            triage_result = await triage_engine.triage_xray(
                image_base64, 
                image_type
            )
            
            # Step 2: Generate findings
            logger.info(f"Step 2: Generating findings (urgency: {triage_result['urgency']})...")
            findings_result = await findings_generator.generate_findings(
                image_base64,
                image_type,
                triage_result,
                patient_age,
                clinical_indications
            )
            
            # Step 3: Generate full report
            logger.info("Step 3: Generating full report...")
            report_result = await report_engine.generate_report(
                findings_payload=findings_result["findings"],
                image_type=image_type,
                triage_info=triage_result
            )
            
            # Calculate totals
            total_cost = triage_result["cost"] + findings_result["cost"] + report_result["cost"]
            processing_time = time.time() - start_time
            
            logger.info(
                f"Analysis complete: {findings_result['model_used']}, "
                f"${total_cost:.4f}, {processing_time:.2f}s"
            )
            
            return {
                "triage": triage_result,
                "findings": findings_result["findings"],
                "report": report_result["report"],
                "model_used": findings_result["model_used"],
                "total_cost": total_cost,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Analysis pipeline error: {e}")
            raise

# Global instance
xray_router = XRayRouter()