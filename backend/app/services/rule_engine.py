"""
Rule Validation Engine
=======================
Per the spec, the AI's raw detections must NEVER directly decide PASS/FAIL.
This module compares AI output against a product's manufacturing
specification and produces a structured decision with:

  status                (PASS / FAIL)
  confidence
  reasons                (list of human-readable reasons)
  severity                (none / minor / major / critical)
  suggested_corrections  (list)
  defects                 (list of structured defect records)

Specification format (Product.specification JSON column), example:
{
  "components": {"bolt": 8, "valve": 1, "cover": 1},
  "position_tolerance_px": 15,
  "critical_defect_types": ["crack", "broken_component", "missing_component"],
  "minor_defect_types": ["scratch"],
  "major_defect_types": ["dent", "rust", "misalignment"]
}
"""
from typing import Any


DEFAULT_CRITICAL_DEFECTS = {"crack", "broken_component", "missing_component"}
DEFAULT_MAJOR_DEFECTS = {"dent", "rust", "misalignment", "surface_damage"}
DEFAULT_MINOR_DEFECTS = {"scratch"}

SEVERITY_ORDER = {"none": 0, "minor": 1, "major": 2, "critical": 3}


def _severity_for_defect(defect_type: str, spec: dict) -> str:
    critical = set(spec.get("critical_defect_types", DEFAULT_CRITICAL_DEFECTS))
    major = set(spec.get("major_defect_types", DEFAULT_MAJOR_DEFECTS))
    minor = set(spec.get("minor_defect_types", DEFAULT_MINOR_DEFECTS))

    if defect_type in critical:
        return "critical"
    if defect_type in major:
        return "major"
    if defect_type in minor:
        return "minor"
    return "minor"  # unknown defect types default to minor rather than silently passing


def evaluate(ai_output: dict[str, Any], specification: dict[str, Any]) -> dict[str, Any]:
    """
    Main entry point. Takes the raw AI output (from ai_inference.run_full_pipeline)
    and the product's specification, returns the full rule-engine decision.
    """
    reasons: list[str] = []
    suggested_corrections: list[str] = []
    structured_defects: list[dict[str, Any]] = []
    worst_severity = "none"
    confidences: list[float] = []

    # ---- 1. Component count / presence check ----
    expected_components: dict[str, int] = specification.get("components", {})
    detected_counts: dict[str, int] = {}
    for det in ai_output.get("component_detections", []):
        detected_counts[det["class"]] = detected_counts.get(det["class"], 0) + 1
        confidences.append(det["confidence"])

    for component_name, expected_qty in expected_components.items():
        found_qty = detected_counts.get(component_name, 0)
        if found_qty < expected_qty:
            missing = expected_qty - found_qty
            reasons.append(f"Missing {missing} x {component_name} (expected {expected_qty}, found {found_qty})")
            suggested_corrections.append(f"Add missing {component_name}")
            structured_defects.append({
                "defect_type": "missing_component",
                "component_name": component_name,
                "location": None,
                "severity": "critical",
                "confidence": None,
                "suggested_correction": f"Add missing {component_name}",
            })
            worst_severity = _worse(worst_severity, "critical")
        elif found_qty > expected_qty:
            reasons.append(f"Unexpected extra {component_name} detected (expected {expected_qty}, found {found_qty})")
            suggested_corrections.append(f"Verify extra {component_name} is not a foreign object")
            worst_severity = _worse(worst_severity, "major")

    # ---- 2. Defect detection results ----
    for det in ai_output.get("defect_detections", []):
        defect_type = det["class"]
        severity = _severity_for_defect(defect_type, specification)
        confidences.append(det["confidence"])
        correction = _suggested_correction_for_defect(defect_type)
        reasons.append(f"{defect_type.replace('_', ' ').title()} detected"
                        + (f" near {det.get('component_name')}" if det.get("component_name") else ""))
        suggested_corrections.append(correction)
        structured_defects.append({
            "defect_type": defect_type,
            "component_name": det.get("component_name"),
            "location": {"bbox": det.get("bbox")},
            "severity": severity,
            "confidence": det.get("confidence"),
            "suggested_correction": correction,
        })
        worst_severity = _worse(worst_severity, severity)

    # ---- 3. Product identity check (Module 1) ----
    product_detections = ai_output.get("product_detections", [])
    if ai_output.get("modules_trained", {}).get("product_detection") and not product_detections:
        reasons.append("Product not detected in frame — check camera positioning")
        suggested_corrections.append("Recapture image with product fully in frame")
        worst_severity = _worse(worst_severity, "critical")

    # ---- 4. Position / tolerance checks (Module 4 - Assembly Validation) ----
    tolerance_px = specification.get("position_tolerance_px")
    if tolerance_px is not None:
        for det in ai_output.get("component_detections", []):
            expected_pos = specification.get("expected_positions", {}).get(det["class"])
            if expected_pos and det.get("bbox"):
                cx = (det["bbox"][0] + det["bbox"][2]) / 2
                cy = (det["bbox"][1] + det["bbox"][3]) / 2
                dx = abs(cx - expected_pos.get("x", cx))
                dy = abs(cy - expected_pos.get("y", cy))
                if dx > tolerance_px or dy > tolerance_px:
                    reasons.append(f"{det['class']} shifted beyond allowed tolerance ({tolerance_px}px)")
                    suggested_corrections.append(f"Realign {det['class']}")
                    structured_defects.append({
                        "defect_type": "misalignment",
                        "component_name": det["class"],
                        "location": {"bbox": det.get("bbox")},
                        "severity": "major",
                        "confidence": det.get("confidence"),
                        "suggested_correction": f"Realign {det['class']}",
                    })
                    worst_severity = _worse(worst_severity, "major")

    # ---- 5. Final decision ----
    status = "FAIL" if reasons else "PASS"
    if not reasons:
        reasons.append("All components present, correctly positioned, and no defects detected")

    overall_confidence = round(sum(confidences) / len(confidences), 4) if confidences else 0.95

    return {
        "status": status,
        "confidence": overall_confidence,
        "severity": worst_severity,
        "reasons": reasons,
        "suggested_corrections": suggested_corrections,
        "defects": structured_defects,
    }


def _worse(a: str, b: str) -> str:
    return a if SEVERITY_ORDER[a] >= SEVERITY_ORDER[b] else b


def _suggested_correction_for_defect(defect_type: str) -> str:
    mapping = {
        "scratch": "Inspect visually; polish if within cosmetic limits",
        "crack": "Reject unit — remove from line for root-cause analysis",
        "dent": "Reject or rework depending on depth; re-inspect",
        "rust": "Reject unit — check storage/handling conditions",
        "broken_component": "Replace broken component and reinspect",
        "missing_component": "Add missing component and reinspect",
        "misalignment": "Realign component to specification and reinspect",
        "surface_damage": "Rework surface or reject depending on severity",
    }
    return mapping.get(defect_type, "Reinspect product")
