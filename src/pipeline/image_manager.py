"""
ImageManager - 에피소드 이미지 자산 관리자
- outputs/epXXX/images/ 폴더의 수동 배치 이미지 인식
- manifest.json 자동 생성 및 관리
- 다중 소스 품질 비교 지원
- 후속 비디오 파이프라인 연동을 위한 선택 이미지 제공
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime


class ImageManager:
    """에피소드 이미지를 수동/자동 방식 모두 관리합니다."""

    def __init__(self, episode_dir: str):
        self.episode_dir = episode_dir
        self.images_dir = os.path.join(episode_dir, "images")
        self.manifest_path = os.path.join(self.images_dir, "manifest.json")
        self.prompts_path = os.path.join(episode_dir, "prompts", "image_prompts.json")
        os.makedirs(self.images_dir, exist_ok=True)

    def load_prompts(self) -> list:
        """image_prompts.json에서 프롬프트 로드"""
        if not os.path.isfile(self.prompts_path):
            return []
        with open(self.prompts_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # enhanced_prompts 키가 있으면 사용, 없으면 전체를 리스트로
        if isinstance(data, dict):
            return data.get("enhanced_prompts", [])
        if isinstance(data, list):
            return data
        return []

    def load_manifest(self) -> dict:
        """manifest.json 로드. 없으면 프롬프트 기반으로 골격 생성"""
        if os.path.isfile(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._generate_skeleton()

    def _generate_skeleton(self) -> dict:
        """프롬프트에서 빈 매니페스트 골격 생성"""
        prompts = self.load_prompts()
        scenes = []
        for p in prompts:
            sid = p.get("scene_id", "unknown")
            scenes.append({
                "scene_id": sid,
                "prompt": p.get("prompt", p.get("enhanced_prompt", "")),
                "selected": None,
                "candidates": []
            })
        return {
            "source_test_mode": True,
            "created_at": datetime.now().isoformat(),
            "scenes": scenes
        }

    def scan_images(self) -> dict:
        """
        images/ 폴더를 스캔하여 수동 배치된 이미지를 감지하고 manifest 업데이트.
        파일명 규칙: <SceneID>_<source>.<ext>  (예: S01_nanobanana.png)
        """
        manifest = self.load_manifest()
        scene_map: Dict[str, dict] = {s["scene_id"]: s for s in manifest["scenes"]}

        if not os.path.isdir(self.images_dir):
            return manifest

        for fname in sorted(os.listdir(self.images_dir)):
            # manifest.json 자체는 건너뜀
            if fname == "manifest.json":
                continue
            # 이미지 파일만 처리
            if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                continue

            # 파일명에서 scene_id와 source 추출
            name_without_ext = fname.rsplit(".", 1)[0]
            parts = name_without_ext.split("_", 1)
            scene_id = parts[0].upper()
            source = parts[1] if len(parts) > 1 else "unknown"

            # 매니페스트에 없는 scene_id면 새로 추가
            if scene_id not in scene_map:
                scene_map[scene_id] = {
                    "scene_id": scene_id,
                    "prompt": "",
                    "selected": None,
                    "candidates": []
                }

            # 이미 등록된 파일이면 건너뜀
            existing_files = [c["file"] for c in scene_map[scene_id]["candidates"]]
            if fname not in existing_files:
                file_path = os.path.join(self.images_dir, fname)
                file_size = os.path.getsize(file_path)
                scene_map[scene_id]["candidates"].append({
                    "file": fname,
                    "source": source,
                    "size_bytes": file_size,
                    "quality_score": None,
                    "notes": ""
                })

            # 후보가 1개이고 아직 선택이 안 됐으면 자동 선택
            if len(scene_map[scene_id]["candidates"]) == 1 and not scene_map[scene_id]["selected"]:
                scene_map[scene_id]["selected"] = fname

        manifest["scenes"] = sorted(scene_map.values(), key=lambda s: s["scene_id"])
        manifest["last_scan"] = datetime.now().isoformat()
        self.save_manifest(manifest)
        return manifest

    def save_manifest(self, manifest: dict):
        """manifest.json 저장"""
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    def select_image(self, scene_id: str, filename: str) -> bool:
        """특정 장면의 사용 이미지를 선택"""
        manifest = self.load_manifest()
        for scene in manifest["scenes"]:
            if scene["scene_id"] == scene_id:
                # 파일이 후보 목록에 있는지 확인
                candidate_files = [c["file"] for c in scene["candidates"]]
                if filename not in candidate_files:
                    return False
                scene["selected"] = filename
                self.save_manifest(manifest)
                return True
        return False

    def set_quality_score(self, scene_id: str, filename: str, score: float, notes: str = "") -> bool:
        """특정 이미지의 품질 점수 설정 (1.0 ~ 10.0)"""
        manifest = self.load_manifest()
        for scene in manifest["scenes"]:
            if scene["scene_id"] == scene_id:
                for candidate in scene["candidates"]:
                    if candidate["file"] == filename:
                        candidate["quality_score"] = round(min(max(score, 1.0), 10.0), 1)
                        candidate["notes"] = notes
                        self.save_manifest(manifest)
                        return True
        return False

    def auto_select_best(self) -> dict:
        """각 장면에서 quality_score가 가장 높은 이미지를 자동 선택"""
        manifest = self.load_manifest()
        selections = {}
        for scene in manifest["scenes"]:
            scored = [c for c in scene["candidates"] if c.get("quality_score") is not None]
            if scored:
                best = max(scored, key=lambda c: c["quality_score"])
                scene["selected"] = best["file"]
                selections[scene["scene_id"]] = best["file"]
            elif scene["candidates"] and not scene["selected"]:
                scene["selected"] = scene["candidates"][0]["file"]
                selections[scene["scene_id"]] = scene["candidates"][0]["file"]
        self.save_manifest(manifest)
        return selections

    def get_selected_images(self) -> Dict[str, str]:
        """선택된 이미지 목록 반환 {scene_id: 절대경로}"""
        manifest = self.load_manifest()
        result = {}
        for scene in manifest["scenes"]:
            if scene.get("selected"):
                result[scene["scene_id"]] = os.path.join(
                    self.images_dir, scene["selected"]
                )
        return result

    def get_coverage_report(self) -> dict:
        """이미지 커버리지 리포트"""
        manifest = self.load_manifest()
        total = len(manifest["scenes"])
        selected = sum(1 for s in manifest["scenes"] if s.get("selected"))
        has_candidates = sum(1 for s in manifest["scenes"] if s.get("candidates"))
        missing = [s["scene_id"] for s in manifest["scenes"] if not s.get("candidates")]

        sources: Dict[str, int] = {}
        for s in manifest["scenes"]:
            for c in s.get("candidates", []):
                src = c.get("source", "unknown")
                sources[src] = sources.get(src, 0) + 1

        return {
            "total_scenes": total,
            "images_selected": selected,
            "has_candidates": has_candidates,
            "missing_scenes": missing,
            "coverage_pct": round(selected / total * 100, 1) if total > 0 else 0,
            "ready_for_video": selected == total and total > 0,
            "sources": sources
        }

    def get_source_comparison(self) -> List[dict]:
        """소스별 품질 비교 리포트 (multi-source 테스트용)"""
        manifest = self.load_manifest()
        comparison = []
        for scene in manifest["scenes"]:
            if len(scene["candidates"]) > 1:
                comparison.append({
                    "scene_id": scene["scene_id"],
                    "selected": scene["selected"],
                    "candidates": [
                        {
                            "file": c["file"],
                            "source": c["source"],
                            "quality_score": c.get("quality_score"),
                            "size_kb": round(c.get("size_bytes", 0) / 1024, 1)
                        }
                        for c in scene["candidates"]
                    ]
                })
        return comparison
