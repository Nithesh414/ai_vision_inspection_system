from typing import Any


def evaluate_wheel_prediction(
    class_name: str,
    confidence: float,
    minimum_confidence: float = 0.65,
) -> dict[str, Any]:

    if confidence < minimum_confidence:
        return {
            "decision": "REVIEW",
            "passed": False,
            "wheel_type": "unknown",
            "screw_status": "unknown",
            "severity": "medium",
            "reasons": [
                "Model confidence is below the required threshold"
            ],
            "suggested_actions": [
                "Capture a clearer image",
                "Ensure the complete wheel is visible",
                "Send the inspection for supervisor verification",
            ],
        }

    rules = {
        "front_with_screw": {
            "decision": "PASS",
            "passed": True,
            "wheel_type": "front",
            "screw_status": "present",
            "severity": "none",
            "reasons": [
                "Front wheel detected",
                "Required screw is present",
            ],
            "suggested_actions": [],
        },

        "front_without_screw": {
            "decision": "FAIL",
            "passed": False,
            "wheel_type": "front",
            "screw_status": "missing",
            "severity": "high",
            "reasons": [
                "Front wheel detected without screw",
                "Required screw is missing",
            ],
            "suggested_actions": [
                "Install the missing screw",
                "Repeat the inspection after assembly",
            ],
        },

        "back_with_screw": {
            "decision": "PASS",
            "passed": True,
            "wheel_type": "back",
            "screw_status": "present",
            "severity": "none",
            "reasons": [
                "Back wheel detected",
                "Required screw is present",
            ],
            "suggested_actions": [],
        },

        "back_without_screw": {
            "decision": "FAIL",
            "passed": False,
            "wheel_type": "back",
            "screw_status": "missing",
            "severity": "high",
            "reasons": [
                "Back wheel detected without screw",
                "Required screw is missing",
            ],
            "suggested_actions": [
                "Install the missing screw",
                "Repeat the inspection after assembly",
            ],
        },
    }

    result = rules.get(class_name)

    if result is None:
        return {
            "decision": "REVIEW",
            "passed": False,
            "wheel_type": "unknown",
            "screw_status": "unknown",
            "severity": "medium",
            "reasons": [
                f"Unsupported prediction class: {class_name}"
            ],
            "suggested_actions": [
                "Send the inspection for supervisor verification"
            ],
        }

    return result
