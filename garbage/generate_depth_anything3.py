#!/usr/bin/env python3
"""Generate a DA3-SMALL depth image and NPZ for one RGB photo on CPU."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output-dir", type=Path, help="Default: outputs/da3/<image_stem>")
    args = parser.parse_args()
    image_path = args.image.expanduser().resolve()
    if not image_path.is_file():
        parser.error(f"Image not found: {image_path}")

    os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "matplotlib-da3"))
    import numpy as np
    import torch
    from huggingface_hub import hf_hub_download
    from PIL import Image
    from safetensors.torch import load_model
    from depth_anything_3.cfg import create_object, load_config
    from depth_anything_3.registry import MODEL_REGISTRY
    from depth_anything_3.utils.io.input_processor import InputProcessor
    from depth_anything_3.utils.io.output_processor import OutputProcessor
    from depth_anything_3.utils.visualize import visualize_depth

    # Use the core model to avoid importing unused 3D exporters and CUDA autocast.
    model = create_object(load_config(MODEL_REGISTRY["da3-small"])).to("cpu").eval()
    weights_path = hf_hub_download("depth-anything/DA3-SMALL", "model.safetensors")
    checkpoint = torch.nn.Module()
    checkpoint.add_module("model", model)
    load_model(checkpoint, weights_path, device="cpu")
    images, _, _ = InputProcessor()([str(image_path)], process_res=504)
    with torch.inference_mode():
        prediction = OutputProcessor()(model(images[None].float()))
    output_dir = (args.output_dir or Path("outputs") / "da3" / image_path.stem).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    arrays = {
        key: getattr(prediction, key)
        for key in ("depth", "conf", "intrinsics", "extrinsics")
        if getattr(prediction, key, None) is not None
    }
    np.savez_compressed(output_dir / "results.npz", **arrays)
    Image.fromarray(visualize_depth(prediction.depth[0])).save(output_dir / "depth.jpg", quality=95)
    print(f"depth_image: {output_dir / 'depth.jpg'}")
    print(f"depth_npz: {output_dir / 'results.npz'}")


if __name__ == "__main__":
    main()
