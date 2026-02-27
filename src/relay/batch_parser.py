"""
배치 응답 파서
- ---[RES-XXX | OwnerName]--- 구분자로 응답을 분리
- JSON 응답은 자동 파싱, 텍스트 응답은 그대로 반환
"""

import re
import json
from typing import Dict, Optional


class ParsedResponse:
    """파싱된 개별 응답"""
    def __init__(self, res_id: str, owner: str, raw_text: str, 
                 parsed_json: Optional[dict] = None):
        self.res_id = res_id
        self.owner = owner
        self.raw_text = raw_text
        self.parsed_json = parsed_json
        self.is_json = parsed_json is not None


class BatchParser:
    """배치 응답을 파싱하여 각 에이전트별 결과로 분배합니다."""

    # RES 블록을 찾는 정규식 패턴
    BLOCK_PATTERN = re.compile(
        r'---\[RES-(\d+)\s*\|\s*([^\]]+)\]---\s*'
        r'(.*?)'
        r'---\[END\s+RES-\1\]---',
        re.DOTALL
    )

    def parse(self, raw_response: str) -> Dict[str, ParsedResponse]:
        """
        전체 응답 텍스트를 파싱하여 {res_id: ParsedResponse} 딕셔너리를 반환합니다.
        """
        results = {}
        
        matches = self.BLOCK_PATTERN.findall(raw_response)
        
        if not matches:
            # 패턴 매칭 실패 시 유연한 파싱 시도
            return self._fallback_parse(raw_response)

        for num, owner, content in matches:
            res_id = f"RES-{num}"
            owner = owner.strip()
            content = content.strip()
            
            # JSON 추출 시도
            parsed_json = self._extract_json(content)
            
            results[res_id] = ParsedResponse(
                res_id=res_id,
                owner=owner,
                raw_text=content,
                parsed_json=parsed_json
            )
        
        return results

    def _extract_json(self, text: str) -> Optional[dict]:
        """텍스트에서 JSON 객체를 추출합니다."""
        # ```json ... ``` 블록 우선 탐색
        json_block = re.search(r'```json\s*(.*?)```', text, re.DOTALL)
        if json_block:
            try:
                return json.loads(json_block.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # ``` ... ``` 블록 탐색
        code_block = re.search(r'```\s*(.*?)```', text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # 중괄호 범위로 직접 JSON 추출
        brace_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass
        
        return None

    def _fallback_parse(self, raw_response: str) -> Dict[str, ParsedResponse]:
        """
        구분자가 정확하지 않을 때의 유연한 파싱.
        RES-XXX 패턴을 느슨하게 매칭합니다.
        """
        results = {}
        
        # 느슨한 패턴: RES-숫자와 owner를 찾고, 다음 RES나 END까지를 내용으로 간주
        loose_pattern = re.compile(
            r'(?:---\s*\[?\s*)?RES-(\d+)\s*[\|\:]?\s*([^\]\-\n]+?)(?:\s*\]?\s*---)?'
            r'\s*(.*?)(?=(?:---\s*\[?\s*)?RES-\d+|$)',
            re.DOTALL | re.IGNORECASE
        )
        
        matches = loose_pattern.findall(raw_response)
        for num, owner, content in matches:
            res_id = f"RES-{num}"
            owner = owner.strip().rstrip(']').strip()
            content = re.sub(r'---\[END\s+RES-\d+\]---', '', content).strip()
            
            if content:
                parsed_json = self._extract_json(content)
                results[res_id] = ParsedResponse(
                    res_id=res_id,
                    owner=owner,
                    raw_text=content,
                    parsed_json=parsed_json
                )
        
        return results

    def get_by_owner(self, results: Dict[str, ParsedResponse], 
                     owner_keyword: str) -> Optional[ParsedResponse]:
        """Owner 이름(부분 매칭)으로 응답을 찾습니다."""
        for resp in results.values():
            if owner_keyword.lower() in resp.owner.lower():
                return resp
        return None
