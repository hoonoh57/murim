SCAIL-2 isolated experiment (RTX 4070 Laptop / 8 GB VRAM)

Run INSTALL-SCAIL2.cmd ONE TIME from E:\comfyui-scail.
On retry, run the SAME file. Downloads resume from .part; no other installation is changed.

Source pins:
 Comfy-Org/ComfyUI v0.33.1, commit 72865f4f27eaf5396f8f36370e0a2be3a9a090ee
 dvelm/SCAIL-2-Unlimited-Video-Low-VRAM commit 2a0d3c0d613e206b4222d61462cf214304488ffd
 city96/ComfyUI-GGUF commit 6ea2651e7df66d7585f6ffee804b20e92fb38b8a
 Kosinkadink/ComfyUI-VideoHelperSuite commit 4d907bee61e92c2e65af3bd6383a4e4d356126d1
 kijai/ComfyUI-KJNodes commit aa2b5ea5e7f61b51f5d26d726f23c1d74e951016
 PyTorch 2.8.0 CUDA 12.6, Python 3.12.

Existing E:\ComfyUI_New is NOT modified. Shared weights are referenced through
ComfyUI\extra_model_paths.yaml; no large file junction and no model copying.
SCAIL-specific models are downloaded from the source repo's documented HF URLs.

After setup: new ComfyUI HTTP server is at http://127.0.0.1:8189.
The preserved upstream workflow is in SCAIL-2-LowVRAM-Recipe\workflows\.
Derived model-file selection only: ComfyUI\user\default\workflows\SCAIL-2-Q3-8GB-FIRST-TEST.json
It uses Q3_K_M and requests 2 seconds. (Native internal segment may be 81 frames.)
The installer stages the upstream SCAIL-2 animation_001 reference + driving
video as a reproducible OFFICIAL NON-MARTIAL DEMO. It converts upstream ref.jpg
to a genuine PNG. The user's Murim portrait is saved separately under
  ComfyUI\input\murim_character_reference.png
Open SCAIL-2-Q3-8GB-FIRST-TEST.json in the new ComfyUI (port 8189), then Queue
one time to compare this original official demo to the upstream example.
For martial arts replace input\your_driving_video.mp4 with a LICENSED sword
motion clip, and select a suitable matching reference image. This is a distinct
quality test; no result is automatically called a successful sword animation.
The installer never queues a GPU render without review.

Report: setup-report.json
Log: logs\install-scail2.log
Failures: source/output preserved, .part model downloads preserved for retry.
