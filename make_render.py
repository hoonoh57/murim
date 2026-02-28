import os
eps=[d for d in os.listdir("outputs") if d.startswith("ep")]
print("episodes:",eps)
ep=eps[0] if eps else None
print("using:",ep)
