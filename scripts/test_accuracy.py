"""Test accuracy on 20 X-ray samples"""
import asyncio
import base64
from pathlib import Path
from app.core.router import xray_router

async def test_accuracy():
    """Run accuracy test on sample X-rays"""
    
    # Load test images (you'll add these)
    test_cases = [
        {"path": "tests/fixtures/sample_xrays/normal_1.jpg", "diagnosis": "Normal"},
        {"path": "tests/fixtures/sample_xrays/cardiomegaly_1.jpg", "diagnosis": "Cardiomegaly"},
        # Add 18 more...
    ]
    
    results = []
    
    for case in test_cases:
        # Read image
        with open(case["path"], "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()
        
        # Analyze
        result = await xray_router.analyze_xray(image_base64)
        
        # Check if diagnosis matches
        report = result["report"].lower()
        diagnosis = case["diagnosis"].lower()
        
        correct = diagnosis in report if diagnosis != "normal" else "no acute" in report
        
        results.append({
            "case": case["diagnosis"],
            "model": result["model_used"],
            "correct": correct,
            "cost": result["total_cost"]
        })
        
        print(f"Case: {case['diagnosis']}, Model: {result['model_used']}, Correct: {correct}")
    
    # Summary
    accuracy = sum(r["correct"] for r in results) / len(results)
    avg_cost = sum(r["cost"] for r in results) / len(results)
    
    print(f"\nAccuracy: {accuracy:.1%}")
    print(f"Average cost: ${avg_cost:.4f}")

if __name__ == "__main__":
    asyncio.run(test_accuracy())