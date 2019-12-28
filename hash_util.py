import hashlib
import json

def hash_string256(msg):
    return hashlib.sha256(msg).hexdigest()

def hash_block(block):
    #returns the HEX string representing the hash
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    # print(hashable_block)
    return hash_string256(json.dumps(hashable_block, sort_keys=True).encode())



