"""
VideoComparator - WAN 2.2 vs LTX-2 품질 비교 자동화
6개 장면을 두 모델로 각각 생성하고 결과를 정리합니다.
"""

import os
import json
import shutil
import time
from typing import Optional
from src.pipeline.comfyui_client import ComfyUIClient
from src.pipeline.prompt_combiner import PromptCombiner


class VideoComparator:
    """두 모델의 비디오 생성 결과를 비교합니다."""

    def __init__(self, episode_dir: str, comfyui_url: str = "http://127.0.0.1:8188"):
        self.episode_dir = episode_dir
        self.client = ComfyUIClient(comfyui_url)
        self.combiner = PromptCombiner(episode_dir)
        self.results_dir = os.path.join(episode_dir, "video_comparison")
        os.makedirs(self.results_dir, exist_ok=True)

    def run_comparison(
        self,
        scenes: Optional[list] = None,
        models: Optional[list] = None,
        width: int = 512,
        height: int = 320,
        frames: int = 41,
    ) -> dict:
        """
        지정된 장면들을 지정된 모델들로 생성하여 비교합니다.
        
        scenes: ["S01", "S02", ...] 또는 None (전체)
        models: ["wan22", "ltx2"] 또는 None (전체)
        """
        if models is None:
            models = ["wan22", "ltx2"]

        all_scenes = self.combiner.get_all_scenes()
        if scenes:
            all_scenes = [s for s in all_scenes if s["scene_id"] in scenes]

        comparison = {
            "episode_dir": self.episode_dir,
            "settings": {
                "width": width,
                "height": height,
                "frames": frames,
            },
            "results": [],
        }

        for scene in all_scenes:
            sid = scene["scene_id"]
            motion_prompt = scene.get("motion_prompt", "")
            image_path = self._find_scene_image(sid)

            if not image_path:
                print(f"  ⚠ {sid}: 이미지 없음, 건너뜀")
                continue

            for model in models:
                print(f"\n{'='*50}")
                print(f"  생성 중: {sid} / {model}")
                print(f"  프롬프트: {motion_prompt[:80]}...")
                print(f"{'='*50}")

                start_time = time.time()
                try:
                    if model == "wan22":
                        output = self.client.generate_wan22(
                            image_path=image_path,
                            prompt=motion_prompt,
                            negative_prompt="blurry, low quality, distorted",
                            width=width,
                            height=height,
                            frames=frames,
                            steps=20,
                        )
                    elif model == "ltx2":
                        output = self.client.generate_ltx2(
                            image_path=image_path,
                            prompt=motion_prompt,
                            width=width,
                            height=height,
                            frames=frames,
                            steps=8,  # Distilled
                        )
                    else:
                        continue

                    elapsed = time.time() - start_time

                    # 결과 파일 복사
                    dest_filename = f"{sid}_{model}.mp4"
                    dest_path = os.path.join(self.results_dir, dest_filename)
                    comfyui_output = os.path.join(
                        self._find_comfyui_root(), output
                    )
                    if os.path.isfile(comfyui_output):
                        shutil.copy2(comfyui_output, dest_path)

                    result = {
                        "scene_id": sid,
                        "model": model,
                        "status": "success",
                        "generation_time_sec": round(elapsed, 1),
                        "output_file": dest_filename,
                        "prompt": motion_prompt,
                        "quality_score": None,  # 수동 평가용
                        "motion_score": None,
                        "audio_score": None if model != "ltx2" else None,
                        "notes": "",
                    }

                except Exception as e:
                    elapsed = time.time() - start_time
                    result = {
                        "scene_id": sid,
                        "model": model,
                        "status": "failed",
                        "error": str(e),
                        "generation_time_sec": round(elapsed, 1),
                    }

                comparison["results"].append(result)
                print(f"  → {result['status']} ({elapsed:.1f}초)")

        # 결과 저장
        report_path = os.path.join(self.results_dir, "comparison_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(comparison, f, ensure_ascii=False, indent=2)

        self._print_summary(comparison)
        return comparison

    def _find_scene_image(self, scene_id: str) -> Optional[str]:
        """장면 이미지 파일 찾기"""
        images_dir = os.path.join(self.episode_dir, "images")
        if not os.path.isdir(images_dir):
            return None
        for fname in os.listdir(images_dir):
            if fname.startswith(scene_id) and fname.endswith((".png", ".jpg", ".webp")):
                return os.path.join(images_dir, fname)
        return None

    def _find_comfyui_root(self) -> str:
        """ComfyUI 설치 루트 경로 (환경에 맞게 수정)"""
        return os.getenv("COMFYUI_ROOT", r"E:\ComfyUI_windows_portable\ComfyUI")

    def _print_summary(self, comparison: dict):
        """결과 요약 출력"""
        print("\n" + "=" * 60)
        print("  비디오 생성 비교 결과 요약")
        print("=" * 60)

        for r in comparison["results"]:
            status = "✅" if r["status"] == "success" else "❌"
            model = r["model"].upper()
            time_str = f"{r['generation_time_sec']}s"
            print(f"  {status} {r['scene_id']} | {model:6s} | {time_str:>8s}")

        print("=" * 60)
        print(f"  결과 폴더: {self.results_dir}")
        print(f"  리포트: comparison_report.json")
