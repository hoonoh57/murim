import time
from typing import Optional, Callable
from src.relay.relay_client import RelaySession

class RelayAutomator:
    """RelaySession을 자동으로 진행시키는 자동화 클래스"""

    def __init__(self, session: RelaySession, ai_client):
        """
        session: RelaySession 인스턴스
        ai_client: generate_response(prompt) 메서드를 가진 객체 (예: GeminiFreeClient)
        """
        self.session = session
        self.ai_client = ai_client

    def run_all(self, max_reworks: int = 2) -> dict:
        """Automate draft preparation only; production belongs to approved Studio."""
        if type(max_reworks) is not int or max_reworks < 0:
            raise ValueError("Invalid rework limit")
        self.session.max_reworks = min(self.session.max_reworks, max_reworks)
        prompt = self.session.start_round1()
        result = self.session.process_round1_response(self.ai_client.generate_response(prompt))
        if not result.get("success"):
            self.session.hold("초안 응답을 확인하지 못했습니다.")
            return self.session.get_summary()
        while True:
            prompt = self.session.start_round2()
            evaluation = self.session.process_round2_response(self.ai_client.generate_response(prompt))
            if not evaluation.get("success") or evaluation.get("killed"):
                return self.session.get_summary()
            prompt = self.session.start_round3()
            if prompt is None:
                return self.session.get_summary()
            result = self.session.process_round3_response(self.ai_client.generate_response(prompt))
            if not result.get("success") or not result.get("reworked"):
                return self.session.get_summary()

if __name__ == "__main__":
    # Example usage for manual CLI run
    from src.api.ai_clients import GeminiFreeClient
    import os
    
    # Needs valid GOOGLE_API_KEY as env var
    client = GeminiFreeClient()
    session = RelaySession(topic="무협의 정점", events="마교 부활")
    automator = RelayAutomator(session, client)
    
    summary = automator.run_all()
    print("--- DRAFT PREPARATION STOPPED ---")
    print(f"Status: {summary['status']}")
    print(f"Title: {summary['scenario'].get('title') if summary['scenario'] else 'N/A'}")
