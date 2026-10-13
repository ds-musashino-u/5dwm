#!/usr/bin/env python3
"""Estimate visible litter count and garbage density from one RGB image."""

from __future__ import annotations

import argparse
import base64
import json
import math
import mimetypes
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


VISIBLE_GARBAGE_PROMPT = """Identify and count visible discarded litter in one RGB photo.

Scope:
- Evaluate only objects resting on the ground or surface shown in the photo.
- This stage is observation only. Do not estimate an area, extrapolate beyond the frame, or use depth information.
- Scan the whole image systematically from top-left to bottom-right before deciding that the candidate list is complete.

Candidate classification:
- List a human-made object as garbage only when its visual identity is sufficiently clear and there is positive evidence that it is discarded litter.
- Typical garbage categories include bottles, cans, cups, wrappers, cartons, disposable containers, paper waste, and cigarette butts.
- Do not classify an object as garbage based only on color, size, silhouette, or because it lies on the ground. Descriptions such as "small dark object", "small light object", "blue item", or "container-like object" are insufficient.
- Classify a plausible litter candidate as uncertain when the image does not clearly distinguish discarded litter from equipment, a personal belonging, or another non-garbage object. Uncertain objects are not counted.
- Classify measurement tools, tape reels, cords, loops, straps, survey markers, attached components, permanent fixtures, vehicles, and personal belongings as non_garbage.
- Objects clearly held, worn, connected to, touched, inspected, or actively used by a person are non_garbage.
- Proximity to a person alone does not determine the result. Use visible evidence of disposal or active use; otherwise classify the object as uncertain.
- Ignore leaves, branches, stones, soil, and other natural material unless a local definition explicitly treats them as waste.

Counting:
- Count each distinct physical garbage item exactly once.
- Count visually distinct adjacent bottles, cans, cups, wrappers, or containers separately.
- For a cluster, use quantity greater than one only when the individual items are visually separable; otherwise mark the cluster uncertain.
- Zero candidates and zero garbage items are valid outcomes. Do not invent a candidate to avoid returning zero.
- candidate_items should include only plausible human-made litter candidates or objects likely to be confused with litter, not every object in the scene.
- Return valid JSON only, matching the requested schema.
"""

AREA_PROMPT = """Estimate the visible ground surface area in this RGB photo in square meters.
- Include only visible ground or surveyed surfaces; exclude sky, open water, and occluded ground.
- Use perspective and recognizable scale references to make a rough estimate.
- Return null for visible_area_estimate_sqm if there is no usable visible ground or no defensible estimate.
- Auxiliary Depth Anything data, when supplied, is relative depth, not meters.
- Use depth only to support geometry, perspective, and visible ground extent.
- Never use depth to identify or classify garbage. Do not infer absolute scale from relative depth values.
- Reflect unknown scale and poor visibility in area_confidence and explain the estimate in reason.
- Return valid JSON only, matching the requested schema.
"""

VISIBLE_GARBAGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "candidate_items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "location": {"type": "string"},
                    "category": {"type": "string"},
                    "classification": {
                        "type": "string",
                        "enum": ["garbage", "uncertain", "non_garbage"],
                    },
                    "quantity": {"type": "integer", "minimum": 1},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "evidence": {"type": "string"},
                },
                "required": [
                    "location", "category", "classification", "quantity", "confidence", "evidence",
                ],
            },
        },
        "visible_count_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "needs_retake": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "required": ["candidate_items", "visible_count_confidence", "needs_retake", "reason"],
}

AREA_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "visible_area_estimate_sqm": {"type": ["number", "null"], "minimum": 0},
        "area_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string"},
    },
    "required": ["visible_area_estimate_sqm", "area_confidence", "reason"],
}


def image_input(path: Path, detail: str = "original") -> dict[str, str]:
    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Use a JPEG, PNG, or WebP image.")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return {
        "type": "input_image",
        "image_url": f"data:{mime_type};base64,{encoded}",
        "detail": detail,
    }


def summarize_depth(path: Path) -> str:
    import numpy as np

    def stats(array: Any) -> dict[str, Any]:
        values = array[np.isfinite(array)]
        if not values.size:
            return {"valid_ratio": 0}
        return {
            "valid_ratio": float(values.size / array.size),
            "min": float(values.min()),
            "percentiles_10_25_50_75_90": np.percentile(values, [10, 25, 50, 75, 90]).tolist(),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "std": float(values.std()),
        }

    with np.load(path, allow_pickle=False) as data:
        depth = data["depth"]
        frame = depth[0] if depth.ndim == 3 else depth
        if frame.ndim != 2 or not frame.size:
            raise ValueError("Depth data must contain a nonempty 2D depth frame.")
        height, width = frame.shape
        center = frame[height // 4:3 * height // 4, width // 4:3 * width // 4]
        summary = {
            "depth": stats(frame),
            "top": stats(frame[:max(1, height // 3)]),
            "bottom": stats(frame[2 * height // 3:]),
            "center": stats(center),
        }
        if "conf" in data:
            summary["conf"] = stats(data["conf"])
        if "intrinsics" in data:
            summary["intrinsics_pixels"] = data["intrinsics"].tolist()

    return "Auxiliary DA3-SMALL relative depth (not meters):\n" + json.dumps(summary)


def request_json(
    client: OpenAI,
    model: str,
    reasoning_effort: str,
    content: list[dict[str, Any]],
    name: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    response = client.responses.create(
        model=model,
        reasoning={"effort": reasoning_effort},
        input=[{"role": "user", "content": content}],
        text={"format": {"type": "json_schema", "name": name, "schema": schema, "strict": True}},
    )
    if response.status != "completed" or not response.output_text:
        raise RuntimeError(f"No completed JSON response for {name}: {response.status}")
    return json.loads(response.output_text)


def estimate_garbage_index(
    image_path: Path,
    model: str = "gpt-6-astra",
    reasoning_effort: str = "high",
    depth_dir: Path | None = None,
) -> dict[str, Any]:
    rgb = image_input(image_path)
    area_content = [{"type": "input_text", "text": AREA_PROMPT}, rgb]
    if depth_dir is not None:
        npz_path = depth_dir / "results.npz"
        depth_image_path = depth_dir / "depth.jpg"
        if not npz_path.is_file() or not depth_image_path.is_file():
            raise FileNotFoundError(f"Missing results.npz or depth.jpg in {depth_dir}; run generate_depth_anything3.py first.")
        area_content.extend([
            {"type": "input_text", "text": summarize_depth(npz_path)},
            image_input(depth_image_path, detail="low"),
        ])

    client = OpenAI()
    observation = request_json(
        client, model, reasoning_effort,
        [{"type": "input_text", "text": VISIBLE_GARBAGE_PROMPT}, rgb],
        "visible_garbage_observation", VISIBLE_GARBAGE_SCHEMA,
    )
    area_result = request_json(
        client, model, reasoning_effort, area_content, "visible_ground_area", AREA_SCHEMA,
    )
    candidates = observation["candidate_items"]
    count = sum(item["quantity"] for item in candidates if item["classification"] == "garbage")
    ambiguous = sum(item["quantity"] for item in candidates if item["classification"] == "uncertain")
    area = area_result["visible_area_estimate_sqm"]
    if area is not None and (not math.isfinite(area) or area <= 0):
        area = None
    return {
        "visible_garbage_count": count,
        "ambiguous_item_count": ambiguous,
        "visible_area_estimate_sqm": area,
        "garbage_density_items_per_sqm": count / area if area is not None else None,
        "candidate_items": candidates,
        "visible_count_confidence": observation["visible_count_confidence"],
        "area_confidence": area_result["area_confidence"],
        "needs_retake": observation["needs_retake"] or area is None,
        "reason": {"visible_count": observation["reason"], "visible_area": area_result["reason"]},
        "image": image_path.name,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "used_depth_anything": depth_dir is not None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--model", default="gpt-5.6-luna")
    parser.add_argument("--reasoning-effort", default="high", choices=["none", "low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--use-depth-anything", action="store_true", help="Use a DA3-SMALL depth image and statistics for area estimation")
    parser.add_argument("--depth-dir", type=Path, help="Depth output directory; enables Depth Anything input")
    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parent / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in .env or the environment.")
    image_path = args.image.expanduser().resolve()
    if not image_path.is_file():
        parser.error(f"Image not found: {image_path}")
    depth_dir = args.depth_dir
    if args.use_depth_anything and depth_dir is None:
        depth_dir = Path("outputs") / "da3" / image_path.stem

    result = estimate_garbage_index(
        image_path, args.model, args.reasoning_effort,
        depth_dir.expanduser().resolve() if depth_dir is not None else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
