"""A verification Utility File"""
from utility.hash_util import hash_block, hash_string256
from wallet import Wallet

class Verification:
    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string256(guess)
        #print(guess_hash)
        return guess_hash[0:2] == '00' 

    @classmethod
    def verify_chain(cls, blockchain):
            """verify the current block and return True if the chain is valid one
                 ... here enumerate extracts  INDEX and VALUE for list iterations"""
            # print(blockchain)
            for (index, block) in enumerate(blockchain):
                # print('##### ', blockchain[index-1])
                if index == 0:
                    continue
                if block.previous_hash != hash_block(blockchain[index-1]):
                    return False
                if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                    return False    
            return True

    #to check whether the transaction can be performed or not
    @staticmethod
    def verify_transaction(transaction, get_balance, checkFunds=True):
        if checkFunds :
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else: 
            Wallet.verify_transaction(transaction)
            
    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions ])  

     