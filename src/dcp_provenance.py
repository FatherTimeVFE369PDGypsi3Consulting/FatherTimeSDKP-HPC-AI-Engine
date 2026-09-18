import hashlib
import json
import time

class DigitalCrystalProtocol:
    """
    Binds runtime execution logs and state vectors to SHA-256 cryptographic ledgers 
    stamped with ORCID identity metadata.
    """
    def __init__(self, author="Donald Paul Smith", orcid="0009-0003-7925-1653"):
        self.author = author
        self.orcid = orcid
        self.ledger = []

    def generate_crystal_hash(self, state_dict: dict) -> str:
        payload = {
            "author": self.author,
            "orcid": self.orcid,
            "timestamp": time.time(),
            "state": state_dict
        }
        serialized = json.dumps(payload, sort_keys=True).encode('utf-8')
        sha256_hash = hashlib.sha256(serialized).hexdigest()
        self.ledger.append({"hash": sha256_hash, "payload": payload})
        return sha256_hash
