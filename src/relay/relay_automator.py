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
        """Round 1부터 끝까지 자동 실행합니다."""
        
        # Round 1
        prompt1 = self.session.start_round1()
        res1 = self.ai_client.generate_response(prompt1)
        self.session.process_round1_response(res1)
        
        # Round 2
        prompt2 = self.session.start_round2()
        res2 = self.ai_client.generate_response(prompt2)
        round2_eval = self.session.process_round2_response(res2)
        
        if round2_eval.get("killed"):
            return self.session.get_summary()

        # Rework handling loop
        while round2_eval.get("needs_rework") and self.session.rework_count < max_reworks:
            print(f"[AUTO] Rework triggered (Attempt {self.session.rework_count + 1})")
            prompt3 = self.session.start_round3()
            res3 = self.ai_client.generate_response(prompt3)
            self.session.process_round3_response(res3)
            
            # Re-evaluate in Round 2
            prompt2 = self.session.start_round2()
            res2 = self.ai_client.generate_response(prompt2)
            round2_eval = self.session.process_round2_response(res2)
            
            if round2_eval.get("killed"):
                return self.session.get_summary()

        # If still needs rework but reached max, just force go
        if round2_eval.get("needs_rework"):
            print("[AUTO] Max reworks reached. Forcing GO.")
            prompt3 = self.session.start_round3(force_go=True)
        else:
            prompt3 = self.session.start_round3()
            
        # Final Round 3 (Imaging/Video/etc.)
        res3 = self.ai_client.generate_response(prompt3)
        self.session.process_round3_response(res3)
        
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
    print("--- AUTOMATIC RUN COMPLETE ---")
    print(f"Status: {summary['status']}")
    print(f"Title: {summary['scenario'].get('title') if summary['scenario'] else 'N/A'}")
