class XrayFindingsPrompts:
    """Class for generating X-ray analysis prompts for radiology AI assistant"""
    
    def __init__(self, patient_age: str = None, clinical_indication: str = None, triage_info: dict = None):
        self.patient_age = patient_age
        self.clinical_indication = clinical_indication
        self.triage_info = triage_info
        self.triage_alerts = triage_info.get("preliminary_findings", []) if triage_info else []

    def generate_single_chest_prompt(self, view_type: str) -> tuple:
        """
        Generate prompt for single chest X-ray view analysis
        
        Args:
            view_type: 'PA', 'AP', or 'AP Portable'
            patient_age: Patient age in years
            clinical_indication: Clinical reason for the X-ray
            triage_info: Dictionary of preliminary findings from triage system (optional)
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        
        system = """You are an expert radiologist analyzing chest X-rays. Your ONLY task is to document objective findings.

    CRITICAL RULES:
    1. Document ONLY what you directly observe in the image
    2. Use objective, descriptive language - avoid diagnostic conclusions
    3. If something is not visible or unclear, explicitly state this
    4. Use anatomical precision - specify exact locations
    5. Describe size, shape, density, margins when abnormalities present
    6. NEVER guess or infer findings not visible in the image
    7. Normal findings must be explicitly stated as "normal" or "unremarkable"

    TRIAGE ALERTS (if provided):
    - An automated triage system may flag areas requiring extra attention
    - These are preliminary alerts, NOT confirmed findings
    - You must independently verify each alert by examining the image
    - If you cannot confirm an alert, state: "Alert area examined - [your observation]"
    - Do NOT simply copy alerts as findings without visual confirmation

    OUTPUT FORMAT:
    Structured bullet points organized by anatomical region.

    You are NOT writing a report. You are documenting observations.
    Another radiologist will use your findings to draft the final report."""
        
        # Build triage context section
        triage_context = ""
        if self.triage_alerts and len(self.triage_alerts) > 0:
            triage_context = f"""
    ---
    TRIAGE ALERTS (Require Extra Attention):
    The automated triage system has flagged the following areas for careful examination:
    """
            for i, alert in enumerate(self.triage_alerts, 1):
                triage_context += f"{i}. {alert}\n"
            
            triage_context += """
    IMPORTANT: These are preliminary alerts only. You must:
    - Independently examine each flagged area
    - Confirm or refute based on what you actually see
    - Describe findings objectively regardless of alert
    - If alert area appears normal, explicitly state this

    ---
    """
        
        prompt = f"""Document objective findings from this chest X-ray.

    STUDY INFORMATION:
    - View: {view_type}
    {"- Age: " + str(self.patient_age) + " years" if self.patient_age else ""}
    {"- Indication: " + self.clinical_indication if self.clinical_indication else ""}
    {triage_context}
    OUTPUT REQUIRED:
    Structured findings organized by anatomical region. Use bullet points. Be precise and objective.

    ---

    ## TECHNICAL FACTORS

    - Inspiration:
    - [Count posterior ribs visible - state number]
    - [Adequate if 9-10 ribs, Limited if <8 ribs]

    - Rotation:
    - [Medial clavicular heads equidistant from spinous processes: Yes/No]
    - [If rotated, state direction: rotated to right/left]

    - Penetration:
    - [Vertebral bodies visible through cardiac silhouette: Yes/No/Partially]
    - [Overall penetration: Adequate/Underpenetrated/Overpenetrated]

    - Positioning:
    - [Upright/Supine/Semi-erect - if determinable]
    - [Scapulae projected over lung fields: Yes/No]

    - Image quality limitations:
    - [State any factors limiting diagnostic assessment: motion artifact, low inspiratory effort, rotation, poor penetration, etc.]
    - [If no limitations: "No significant limitations"]

    ---

    ## AIRWAYS

    - Trachea:
    - Position: [Midline/Deviated to right/Deviated to left]
    - Caliber: [Normal/Narrowed/Not well visualized]
    - [If deviated, describe degree: mild/moderate/marked deviation]

    - Carina:
    - [Visible/Not visible on this view]
    - [If visible: Normal angle/Widened]

    - Major bronchi:
    - [Visible/Not well visualized]
    - [Any abnormal lucency or opacity]

    ---

    ## LUNGS AND PLEURAL SPACE

    CRITICAL: Examine lungs and pleura TOGETHER for each zone. Pneumothorax affects both parenchyma and pleural space.

    - Right upper zone:
    - Parenchyma: [Clear / Describe any opacity, mass, nodule, cavitation]
    - Pleural space: [Normal / Pneumothorax - if present, describe size and visible lung edge / Effusion / Thickening]
    - [If pneumothorax: state size (small <2cm/moderate 2-4cm/large >4cm), location of visible lung edge]
    - [If abnormal: location (medial/lateral/central), size estimate, density, margins]

    - Right mid zone:
    - Parenchyma: [Clear / Describe findings]
    - Pleural space: [Normal / Pneumothorax - describe / Effusion / Thickening]

    - Right lower zone:
    - Parenchyma: [Clear / Describe findings]
    - Pleural space: [Normal / Pneumothorax - describe / Effusion / Thickening]
    - Costophrenic angle: [Sharp / Blunted / Obliterated]

    - Left upper zone:
    - Parenchyma: [Clear / Describe findings]
    - Pleural space: [Normal / Pneumothorax - describe / Effusion / Thickening]

    - Left mid zone:
    - Parenchyma: [Clear / Describe findings]
    - Pleural space: [Normal / Pneumothorax - describe / Effusion / Thickening]

    - Left lower zone:
    - Parenchyma: [Clear / Describe findings]
    - Pleural space: [Normal / Pneumothorax - describe / Effusion / Thickening]
    - Costophrenic angle: [Sharp / Blunted / Obliterated]

    - Retrocardiac region:
    - [Clear / Opacity present - describe / Obscured by technical factors]

    - Overall lung assessment:
    - Lung volumes: [Normal / Hyperinflated / Low lung volumes]
    - Hemithorax symmetry: [Symmetric / Asymmetric - describe which side and extent]
    - Vascular markings: [Normal prominence / Increased / Decreased]
    - Distribution: [Normal / Centralized / Peripheral pruning]

    - Interstitial pattern:
    - [None visible / If present: reticular/nodular/reticulonodular/ground-glass]
    - [Distribution if present: upper/lower/diffuse/peripheral]

    - Air bronchograms:
    - [None visible / Present - describe location]

    - Cavitation:
    - [None visible / Present - describe location, size, wall thickness]

    ---

    ## PLEURAL ASSESSMENT SUMMARY

    Review entire pleural space for each hemithorax:

    - Right hemithorax:
    - Overall pleural assessment: [Normal / Pneumothorax / Effusion / Thickening / Calcification]
    - If pneumothorax: [Size (small/moderate/large), extent (apical/lateral/complete), visible lung edge location]
    - If effusion: [Size (small/moderate/large), blunting pattern, meniscus if visible]
    - Pleural thickening: [None / Present - location and extent]
    - Pleural calcification: [None / Present - location]

    - Left hemithorax:
    - Overall pleural assessment: [Normal / Pneumothorax / Effusion / Thickening / Calcification]
    - If pneumothorax: [Size, extent, visible lung edge location]
    - If effusion: [Size, blunting pattern]
    - Pleural thickening: [None / Present - location and extent]
    - Pleural calcification: [None / Present - location]

    - Pleural surfaces:
    - [Smooth bilaterally / Irregular / Nodular - describe if abnormal]

    ---

    ## HEART AND MEDIASTINUM

    - Cardiac silhouette:
    - Size assessment:
        * Visual impression: [Normal / Borderline enlarged / Enlarged]
        * Basis: [Cardiac width relative to thoracic width - clearly less than half/approximately half/clearly more than half]
        * {'Projection note: PA view allows more reliable cardiac size assessment' if view_type == 'PA' else 'Projection note: AP projection may artifactually enlarge cardiac silhouette'}
    - Configuration: [Normal / Globular / Boot-shaped / Other specific shape]
    - Confidence: [High / Moderate / Low]

    - Cardiac borders:
    - Right heart border: [Well-defined / Obscured]
    - [If obscured: suggests right middle lobe or right atrial pathology]
    - Left heart border: [Well-defined / Obscured]
    - [If obscured: suggests lingular or left ventricular pathology]
    - Chamber contours: [Normal / Specific chamber prominence - RA/LA/RV/LV]

    - Mediastinum:
    - Width: [Normal / Widened / Narrow]
    - [If widened: location (superior/middle/entire), approximate width if severely widened]
    - Contours: [Normal / Straightening / Bulging / Mass effect]
    - Superior mediastinum: [Normal / Widened / Deviated]
    - Aortopulmonary window: [Normal lucency / Opacified / Obscured]
    - [If mediastinal shift present: direction and degree]

    - Aorta:
    - Aortic knob: [Normal / Prominent / Calcified / Tortuous / Unfolded]
    - Ascending aorta: [Normal / Prominent / Not visible]
    - Descending aorta: [Normal / Tortuous / Dilated / Unfolded]
    - Calcification: [None / Present - describe location and extent]

    - Hila:
    - Right hilum: [Normal size and contour / Enlarged / Obscured / Mass-like / Displaced]
    - Left hilum: [Normal size and contour / Enlarged / Obscured / Mass-like / Displaced]
    - Symmetry: [Symmetric / Asymmetric - which side affected]
    - Contours: [Smooth / Lobulated / Indistinct]

    ---

    ## BONES

    - Ribs:
    - [Intact bilaterally / Fracture present - specify rib number and location]
    - [If fracture: acute (sharp margins) / healing (callus formation)]
    - [Lytic lesions: None / Present - location]
    - [Sclerotic lesions: None / Present - location]

    - Clavicles:
    - Right: [Intact / Fracture / Healed fracture / Lesion / Surgical changes]
    - Left: [Intact / Fracture / Healed fracture / Lesion / Surgical changes]

    - Scapulae:
    - [Visible portions unremarkable / Describe abnormality]

    - Visible spine:
    - Alignment: [Normal / Scoliosis / Kyphosis / Rotation]
    - Vertebral bodies: [Heights maintained / Compression / Wedging]
    - [Lesions: None / Present - describe]
    - Disc spaces: [Preserved / Narrowed]
    - Degenerative changes: [None / Mild / Moderate / Severe]

    - Shoulders (if visible):
    - [Unremarkable bilaterally / Describe abnormality]

    ---

    ## SOFT TISSUES

    - Chest wall:
    - Symmetry: [Symmetric / Asymmetric - describe]
    - Masses: [None / Present - location, size]
    - Swelling: [None / Present - location, extent]

    - Subcutaneous emphysema:
    - [None visible / Present - location and extent (localized/extensive)]
    - [If present with pneumothorax: note association]

    - Breast shadows:
    - [Symmetric / Asymmetric / Mastectomy / Not applicable]

    - Axillae:
    - [Normal bilaterally / Lymphadenopathy / Mass / Not well visualized]

    ---

    ## LINES, TUBES, AND DEVICES

    [If none: "No lines, tubes, or medical devices visible"]

    - If present, document EACH:
    - Device type: [ETT/NGT/Central line/Pacemaker/ICD/Chest tube/Other]
    - Position and course: [Describe]
    - Tip location: [Specific landmark]
    - Appropriateness: [Appropriate / Suboptimal / Malpositioned - explain]
    - Integrity: [Intact / Fractured / Kinked]

    ---

    ## ADDITIONAL FINDINGS

    - Diaphragm:
    - Right hemidiaphragm:
        * Position: [Normal / Elevated / Flattened / Depressed]
        * Contour: [Smooth dome / Irregular / Tented / Obscured]
    - Left hemidiaphragm:
        * Position: [Normal / Elevated / Flattened / Depressed]
        * Contour: [Smooth dome / Irregular / Tented / Obscured]
    - Gastric bubble: [Visible below left hemidiaphragm / Displaced / Not seen]

    - Subdiaphragmatic region:
    - Free air: [None visible / Present - describe]
    - Bowel gas: [Normal / Abnormal - describe]

    - Incidental findings:
    - [None / Describe findings not fitting above categories]

    ---

    CRITICAL VERIFICATION STEPS:

    1. ✓ If triage alerts were provided, verify you addressed each one:
    - Document what you actually see in each alert area
    - State "confirmed" or "not confirmed" based on your observation
    - Provide objective description regardless of alert

    2. ✓ Cross-check for consistency:
    - If pneumothorax in pleural space → must mention in lung zone parenchyma
    - If subcutaneous emphysema → check for associated pneumothorax
    - If blunted costophrenic angle → check for effusion
    - If mediastinal shift → note direction and look for cause

    3. ✓ Every anatomical section addressed:
    - Use "Normal", "Clear", "Unremarkable", or "Not well visualized"
    - Never skip sections

    4. ✓ Abnormalities fully described:
    - Location, size, density, margins, shape
    - Objective descriptors only - no diagnoses

    5. ✓ If cannot see clearly:
    - State reason: rotation, penetration, overlying structures
    - Do NOT guess

    ---

    OUTPUT FORMAT:
    Return ONLY structured bullet-point findings.
    - No preamble
    - No diagnostic interpretations
    - Just objective findings following the exact format above"""

        return (system, prompt)

    def generate_pa_lateral_chest_prompt(self) -> tuple:
        """
        Generate prompt for PA and lateral chest X-ray analysis
        
        Args:
            patient_age: Patient age in years
            clinical_indication: Clinical reason for the X-ray
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        
        
        system = """You are an expert radiologist AI assistant creating draft chest X-ray reports for Nigerian diagnostic centers.

CRITICAL RULES TO PREVENT ERRORS:
1. ONLY describe findings you can directly see in the images
2. CORRELATE findings between PA and lateral views - do not double-count the same finding
3. If a finding is visible on only one view, explicitly state which view
4. If you cannot see something clearly on either view, state "not clearly visualized" - never guess
5. Use phrases like "appears to show" or "consistent with" rather than definitive statements
6. If image quality limits assessment on any view, explicitly state this
7. NEVER invent findings - absence of description means normal
8. When uncertain, provide differential diagnosis rather than single conclusion

CROSS-VIEW CORRELATION:
- Confirm abnormalities seen on both views (increases confidence)
- Note retrocardiac/retrosternal areas (better seen on lateral)
- Assess hilar structures from both projections
- Evaluate pleural effusions using both views

REPORT STRUCTURE:
- Technique (mention both views)
- Findings (systematic review correlating both views)
- Impression
- Recommendations (if needed)

URGENT FINDINGS TO FLAG:
- Pneumothorax
- Large pleural effusion
- Pneumoperitoneum
- Widened mediastinum (>8cm)
- Tension pneumothorax signs
- Massive consolidation
- Foreign body

Use clear Nigerian English and standard radiology terminology. A qualified radiologist will review all reports before finalization."""
        
        prompt = f"""Analyze this chest X-ray study with PA and lateral views and create a draft radiology report.

TECHNIQUE:
- Two views: PA and Lateral
{"- Patient Age: " + str(self.patient_age) + " years" if self.patient_age else ""}
{"- Clinical Indication: " + self.clinical_indication if self.clinical_indication else ""}

Images provided:
- Image 1: PA view
- Image 2: Lateral view

INSTRUCTIONS:
Provide systematic analysis correlating BOTH views. For each section, describe findings visible on PA, lateral, or both. ONLY describe what you can actually see.

1. TECHNICAL QUALITY (assess both views)
PA view:
- Inspiration (9-10 posterior ribs visible)
- Rotation (clavicular heads equidistant from spine)
- Penetration (vertebrae visible through heart)

Lateral view:
- True lateral positioning (ribs should be superimposed posteriorly)
- Arms adequately raised (scapulae rotated out of lung fields)
- Penetration (spine visible throughout)

If either view has technical limitations, state how this affects interpretation

2. LUNGS AND AIRWAYS (correlate both views)
- Trachea and carina (PA: midline position, Lateral: caliber and course)

- Lung parenchyma by zone:
    * Right upper/middle/lower
    * Left upper/lower
    * Describe location in 3D using both views

- For any opacity/consolidation:
    * "Opacity in [location] on PA view, confirmed on lateral in [anterior/posterior] [upper/middle/lower] segment"
    * This gives 3D localization

- Retrocardiac region (CRITICAL - lateral view shows this best):
    * PA view: check for left heart border silhouetting
    * Lateral view: assess retrocardiac clear space
    * Common pitfall: retrocardiac pneumonia missed on PA alone

- Interstitial patterns: describe distribution on both views

3. PLEURA (correlate both views)
- Costophrenic angles:
    * PA: lateral and medial angles
    * Lateral: posterior costophrenic angle (most sensitive for small effusions)

- Pleural effusion assessment:
    * Small effusion: may be visible only on lateral (blunting of posterior costophrenic angle)
    * Quantify: <300ml (blunts lateral only), 300-500ml (blunts PA), >500ml (meniscus visible)
    * Laterality and size

- Pneumothorax:
    * PA: check apices and lateral margins (upright)
    * Lateral: check anterior costophrenic angle and retrosternal space
    * Quantify if present

4. CARDIAC SILHOUETTE (correlate both views)
- Size:
    * PA view: Cardiothoracic ratio (cardiac width / thoracic width)
    * Normal CTR <0.5 on PA
    * Lateral view: retrosternal space, retrocardiac space

- Borders and chambers:
    * PA: RA (right border), LA appendage (left upper border), LV (left lower border)
    * Lateral: RV (anterior), LV (posterior-inferior)
    * Note if any borders are obscured (silhouette sign) - specify which view

- If cardiomegaly: describe which chambers appear enlarged based on both views

5. MEDIASTINUM (correlate both views)
- Width on PA (measure if >8cm at aortic arch)

- Contours:
    * PA: aortic knob, aortopulmonary window, SVC margin
    * Lateral: aortic arch, retrosternal space, retrotracheal space

- Hilar structures:
    * PA: size, symmetry, lobulation
    * Lateral: anterior vs posterior hilar masses (helps differentiate PA from bronchus mass)

- Retrosternal space (lateral view):
    * Should be clear radiolucent space
    * Loss of retrosternal space suggests anterior mediastinal mass

6. BONES AND SOFT TISSUES
- Thoracic cage: ribs, sternum (better on lateral), thoracic spine
- Fractures, lytic or sclerotic lesions
- Scoliosis or kyphosis
- Soft tissues: emphysema, masses

7. HIDDEN AREAS (use lateral view advantage)
- Retrocardiac space
- Retrosternal space
- Posterior costophrenic angles
- Inferior lingula/left lower lobe

8. LINES AND TUBES (if present)
- Position on both views (confirms depth/trajectory)

IMPRESSION:
Provide concise summary (2-5 sentences):
- Normal or abnormal
- Significant findings in order of importance
- Most likely diagnosis OR differential if uncertain
- Use qualifiers: "consistent with", "suggestive of", "appears to represent"
- Mention if findings are confirmed on both views (increases confidence)

CRITICAL FINDINGS:
If urgent findings present, start with: "**URGENT:**"

RECOMMENDATIONS:
Only if indicated:
- Further imaging
- Clinical correlation
- Comparison with priors
- Follow-up

CROSS-VIEW CORRELATION RULES:
✓ Finding seen on BOTH views → Higher confidence, state this
✓ Finding seen on ONE view only → State which view, explain why (e.g., "opacity visible only on lateral suggests anterior location")
✓ Conflicting findings → Describe discrepancy, suggest technical factor or positioning artifact
✓ DO NOT double-count the same finding from both views

IMPORTANT:
- Only describe visible findings
- State if image quality limits assessment
- Use diagnostic qualifiers when uncertain
- Provide differential diagnosis for ambiguous findings
- Never invent findings"""

        return (system, prompt)



    def generate_limb_prompt(self, view_type: str = "AP and Lateral") -> tuple:
        """
        Generate prompt for limb X-ray analysis
        
        Args:
            view_type: Type of views taken (default: "AP and Lateral")
            patient_age: Patient age in years
            clinical_indication: Clinical reason for the X-ray
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        
        system = """You are an expert radiologist AI assistant creating draft limb X-ray reports for Nigerian diagnostic centers.

CRITICAL RULES:
1. ONLY describe findings you can directly see in the image
2. If you cannot see something clearly, state "not clearly visualized" - never guess
3. Use phrases like "appears to show" or "consistent with" rather than definitive statements
4. If image quality limits assessment, explicitly state this
5. NEVER invent findings
6. When uncertain, provide differential diagnosis

REPORT STRUCTURE:
- Clinical History
- Technique
- Findings (systematic bone, joint, soft tissue review)
- Impression
- Recommendations (if needed)

Use clear Nigerian English and standard radiology terminology. A qualified radiologist will review all reports before finalization."""

        prompt = f"""Analyze this limb X-ray and create a draft radiology report.

CLINICAL HISTORY:
{"- Clinical Indication: " + self.clinical_indication if self.clinical_indication else "- [Not provided]"}
{"- Patient Age: " + str(self.patient_age) + " years" if self.patient_age else ""}

TECHNIQUE:
{view_type} views of [specify anatomical region from image]

FINDINGS:
Systematically describe:

1. BONES:
- Alignment and cortical integrity
- Any fractures (if present, describe location, pattern, displacement)
- Bone density and texture
- Any lytic or sclerotic lesions
- Growth plates (if applicable)

2. JOINTS:
- Joint spaces (widened, narrowed, or normal)
- Articular surfaces alignment
- Presence of effusion
- Degenerative changes

3. SOFT TISSUES:
- Swelling or edema
- Foreign bodies
- Calcifications
- Muscle planes

For fractures, systematically describe:
- Location: proximal/mid/distal third of bone
- Pattern: transverse/oblique/spiral/comminuted/segmental
- Displacement: amount and direction
- Angulation: degrees and direction
- Intra-articular extension: yes/no
- Associated findings: soft tissue swelling, joint effusion

IMPRESSION:
Provide concise summary (2-3 sentences):
- Normal or describe primary abnormality
- Most likely diagnosis or differential if uncertain
- Clinical significance

RECOMMENDATIONS:
Only if indicated:
- Follow-up imaging
- Clinical correlation
- Orthopedic consultation
- Comparison with prior studies

IMPORTANT:
- Only describe visible findings
- State if image quality limits assessment
- Use diagnostic qualifiers when uncertain"""

        return (system, prompt)

    def get_findings_prompt(self, image_type: str, view_type: str = None) -> dict:
        """
        Get appropriate report prompt based on image type by calling the corresponding method
        
        Args:
            image_type: Type of X-ray ('chest_single', 'chest_pa_lateral', 'limb')
            view_type: Specific view type (e.g., 'PA', 'AP', 'AP Portable' for single chest)
            patient_age: Patient age in years
            clinical_indication: Clinical reason for the X-ray
            triage_info: Optional dictionary with urgency and preliminary findings
            
        Returns:
            dict: Dictionary with 'system' and 'user' prompts
        """
        
        
        # Route to appropriate method based on image type
        if image_type == "chest_single":
            if not view_type:
                view_type = "PA"  # Default to PA view
            system, user = self.generate_single_chest_prompt(view_type)
        elif image_type == "chest_pa_lateral":
            system, user = self.generate_pa_lateral_chest_prompt()
        elif image_type == "limb":
            system, user = self.generate_limb_prompt(view_type or "AP and Lateral")
        else:
            # Default to single chest view
            system, user = self.generate_single_chest_prompt("PA")
        

        return {
            "system": system,
            "user": user
        }