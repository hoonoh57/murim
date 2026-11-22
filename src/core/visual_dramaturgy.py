"""Pre-production visual meaning audit: diagnosis, never an aesthetic auto-PASS.

The author should prove what actually changes on screen. A new subtitle or
a different narration over the same framing is not fresh visual information.
This module is independent of GPU/video/format to keep a safe G2 boundary.
"""
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET


def reference_intro_audit(path):
    """Audit one REVIEW_ONLY M-VML shot plan; no claim about rendered quality."""
    root = ET.parse(Path(path)).getroot()
    seq = root.find("sequence")
    if seq is None:
        raise ValueError("Missing visual sequence")
    shots = []
    for s in seq.findall("shot"):
        sec = float(s.get("seconds", "0"))
        if sec <= 0:
            raise ValueError("Invalid shot duration")
        shots.append({
            "id": s.get("id", ""),
            "asset": s.get("asset", ""),
            "framing": s.get("framing", ""),
            "seconds": sec,
            "heading": s.get("heading", ""),
            "visual_focus": s.get("visual-focus", ""),
            "new_visual_information": s.get("new-visual-information", ""),
            "observed_change": s.get("observed-change", ""),
        })
    return audit_shot_plan(shots)


def audit_shot_plan(shots):
    """Return evidence-based issues; no numerical exposure cap or automatic PASS.

    READY_FOR_REAL_VIEWING means the *plan* has sufficient annotations to inspect
    actual frames, not that it looks good or can be produced.
    """
    if not isinstance(shots, list) or not shots:
        raise ValueError("Shot plan must not be empty")
    issues = []
    keyed = defaultdict(list)
    screen = defaultdict(float)
    for number, s in enumerate(shots, 1):
        if not isinstance(s, dict):
            raise ValueError("Shot must be an object")
        sid = s.get("id") or str(number)
        asset, framing = s.get("asset"), s.get("framing")
        if not asset or not framing:
            issues.append({"shot": sid, "code": "VISUAL_SOURCE_UNSPECIFIED", "severity": "HOLD"})
            continue
        try:
            seconds = float(s.get("seconds", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid shot duration") from exc
        if not 0 < seconds <= 3600:
            raise ValueError("Invalid shot duration")
        screen[asset] += seconds
        look = (asset, framing)
        keyed[look].append(s)
        if not s.get("visual_focus") or not s.get("new_visual_information"):
            issues.append({"shot": sid, "code": "NO_VERIFIABLE_VIEWER_DISCOVERY", "severity": "REWORK"})
    for (asset, framing), group in keyed.items():
        if len(group) <= 1:
            continue
        seen = set()
        for s in group:
            signature = (
                " ".join(str(s.get("visual_focus") or "").split()),
                " ".join(str(s.get("new_visual_information") or "").split()),
            )
            # New headings, title cards, or period captions do not establish
            # independent visual changes to an otherwise identical image.
            if not s.get("observed_change") or signature in seen:
                issues.append({
                    "shot": s.get("id", ""), "code": "UNCHANGED_IMAGE_REEXPOSED",
                    "severity": "REWORK", "asset": asset, "framing": framing,
                })
            seen.add(signature)
    # This diagnostic is descriptive, not a threshold that encourages frequent
    # cuts or penalizes an intentionally meaningful held shot.
    return {
        "total_seconds": sum(screen.values()),
        "asset_seconds": dict(screen),
        "issues": issues,
        "status": "REWORK_REQUIRED" if any(i["severity"] == "REWORK" for i in issues)
                  else "EVIDENCE_REQUIRED" if issues else "READY_FOR_REAL_VIEWING",
        "actual_render_review": "NOT_RUN",
    }
