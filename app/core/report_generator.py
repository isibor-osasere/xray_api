"""X-ray report drafting logic"""

from typing import Dict
from app.services.llm_provider import llm_provider
from app.prompts.report_prompts import report_prompts
from app.utils.logger import logger


class ReportEngine:
    """Handles drafting of radiology reports from structured findings"""

    def __init__(self):
        self.llm = llm_provider.format

    async def generate_report(
        self,
        findings_payload: str,
        image_type: str,
        triage_info: Dict = None,
    ) -> Dict:
        """
        Generate Nigerian-style radiology report from structured findings

        Args:
            findings_payload: Full findings output including:
                - EXAMINATION
                - PROJECTION / VIEW
                - STRUCTURED FINDINGS

        Returns:
            {
                "report": str,
                "confidence": float,
                "cost": float
                
            }
        """
        try:
            prompt = report_prompts.get_report_prompt(image_type=image_type)

            messages = [
                {
                    "role": "system",
                    "content": prompt["system"]
                },
                {
                    "role": "user",
                    "content":  f"FINDINGS PAYLOAD:\n{findings_payload}"
                }
            ]

            response = await self.llm.ainvoke(messages)

            report_text = response.content.strip()

            logger.info("Radiology report successfully generated")

            return {
                "report": report_text,
                "triage": triage_info,
                "cost": 0.02          # approx report-generation cost
            }

        except Exception as e:
            logger.error(f"Report generation error: {e}")

            return {
                "report": (
                    "EXAMINATION:\n"
                    "Unable to generate report\n\n"
                    "IMPRESSION:\n"
                    "Automated report generation failed. "
                    "Immediate radiologist review advised."
                ),
                "triage": triage_info,
                "cost": 0.02
            }


# Global instance
report_engine = ReportEngine()
