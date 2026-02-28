"""
ComfyUI API Client - WAN 2.2 / LTX-2 비디오 생성 자동화
Murim AI Content Factory의 Video Agent가 사용합니다.
"""

import os
import io
import json
import time
import uuid
import urllib.request
import urllib.parse

COMFYUI_API = "http://127.0.0.1:8188"


class ComfyUIClient:
    """ComfyUI API를 통한 비디오 생성 클라이언트"""

    def __init__(self, base_url: str = COMFYUI_API):
        self.base_url = base_url

    # ── 기본 API 호출 ──────────────────────────────

    def _post_json(self, endpoint: str, data: dict) -> dict:
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/{endpoint}",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _get_json(self, endpoint: str) -> dict:
        with urllib.request.urlopen(f"{self.base_url}/{endpoint}") as resp:
            return json.loads(resp.read())

    def upload_image(self, image_path: str) -> str:
        """이미지를 ComfyUI에 업로드하고 파일명 반환"""
        filename = os.path.basename(image_path)
        with open(image_path, "rb") as f:
            image_data = f.read()

        # multipart/form-data 수동 구성
        boundary = uuid.uuid4().hex
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + image_data + f"\r\n--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            f"{self.base_url}/upload/image",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        return result.get("name", filename)

    def queue_prompt(self, workflow: dict) -> str:
        """워크플로우를 큐에 추가하고 prompt_id 반환"""
        result = self._post_json("prompt", {"prompt": workflow})
        return result.get("prompt_id", "")

    def get_history(self, prompt_id: str) -> dict:
        """생성 완료 후 결과 히스토리 조회"""
        return self._get_json(f"history/{prompt_id}")

    def wait_for_completion(self, prompt_id: str, timeout: int = 1800) -> dict:
        """생성 완료까지 대기 (기본 30분 타임아웃)"""
        start = time.time()
        while time.time() - start < timeout:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                return history[prompt_id]
            time.sleep(5)  # 5초 간격 폴링
        raise TimeoutError(f"ComfyUI 생성이 {timeout}초 내에 완료되지 않았습니다.")

    # ── WAN 2.2 워크플로우 ──────────────────────────

    def generate_wan22(
        self,
        image_path: str,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 320,
        frames: int = 41,
        steps: int = 20,
    ) -> str:
        """WAN 2.2 I2V 비디오 생성"""
        uploaded = self.upload_image(image_path)
        workflow = self._load_workflow("wan22_5b_api.json")

        # 노드 값 주입 (노드 ID는 워크플로우에 따라 조정 필요)
        workflow = self._inject_values(
            workflow,
            image_filename=uploaded,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            frames=frames,
            steps=steps,
            model_type="wan22",
        )

        prompt_id = self.queue_prompt(workflow)
        result = self.wait_for_completion(prompt_id)
        return self._extract_output_path(result)

    # ── LTX-2 워크플로우 ────────────────────────────

    def generate_ltx2(
        self,
        image_path: str,
        prompt: str,
        width: int = 512,
        height: int = 320,
        frames: int = 41,
        steps: int = 8,  # Distilled 모델은 8스텝
    ) -> str:
        """LTX-2 I2V 비디오+오디오 생성"""
        uploaded = self.upload_image(image_path)
        workflow = self._load_workflow("ltx2_i2v_api.json")

        workflow = self._inject_values(
            workflow,
            image_filename=uploaded,
            prompt=prompt,
            negative_prompt="",
            width=width,
            height=height,
            frames=frames,
            steps=steps,
            model_type="ltx2",
        )

        prompt_id = self.queue_prompt(workflow)
        result = self.wait_for_completion(prompt_id)
        return self._extract_output_path(result)

    # ── 유틸리티 ────────────────────────────────────

    def _load_workflow(self, filename: str) -> dict:
        """workflows/ 폴더에서 API용 워크플로우 JSON 로드"""
        workflow_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "workflows"
        )
        filepath = os.path.join(workflow_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _inject_values(self, workflow: dict, **kwargs) -> dict:
        """워크플로우의 노드 값을 동적으로 교체"""
        # 이 부분은 실제 워크플로우 JSON의 노드 ID에 맞춰 구현
        # ComfyUI에서 워크플로우를 "Save (API Format)"으로 저장하면
        # 노드 ID가 숫자 키로 나옵니다
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")

            # 이미지 로드 노드
            if class_type in ("LoadImage", "LTXVLoadImage"):
                node_data["inputs"]["image"] = kwargs.get("image_filename", "")

            # 프롬프트 노드
            if class_type in ("CLIPTextEncode", "LTXVTextEncode"):
                if "positive" in str(node_data.get("_meta", {}).get("title", "")).lower():
                    node_data["inputs"]["text"] = kwargs.get("prompt", "")
                elif "negative" in str(node_data.get("_meta", {}).get("title", "")).lower():
                    node_data["inputs"]["text"] = kwargs.get("negative_prompt", "")

            # 비디오 크기/길이 노드
            if class_type in ("Wan22ImageToVideoLatent", "EmptyHunyuanLatentVideo",
                               "LTXVEmptyLatent"):
                inputs = node_data.get("inputs", {})
                if "width" in inputs:
                    inputs["width"] = kwargs.get("width", 512)
                if "height" in inputs:
                    inputs["height"] = kwargs.get("height", 320)
                if "length" in inputs:
                    inputs["length"] = kwargs.get("frames", 41)
                if "num_frames" in inputs:
                    inputs["num_frames"] = kwargs.get("frames", 41)

            # KSampler 노드
            if class_type in ("KSampler", "LTXVSampler"):
                if "steps" in node_data.get("inputs", {}):
                    node_data["inputs"]["steps"] = kwargs.get("steps", 20)

        return workflow

    def _extract_output_path(self, history: dict) -> str:
        """히스토리에서 출력 파일 경로 추출"""
        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            if "videos" in node_output:
                video_info = node_output["videos"][0]
                return os.path.join("output", video_info.get("filename", ""))
            if "gifs" in node_output:
                gif_info = node_output["gifs"][0]
                return os.path.join("output", gif_info.get("filename", ""))
        return ""
