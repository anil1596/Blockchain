import hashlib
import json

def hash_string256(msg):
    return hashlib.sha256(msg).hexdigest()

def hash_block(block):
    #returns the HEX string representing the hash
    return hash_string256(json.dumps(block, sort_keys=True).encode())



