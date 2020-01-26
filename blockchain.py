from functools import reduce
from collections import OrderedDict
import json
from block import Block
from transaction import Transaction
from utility.verification import Verification 
from utility.hash_util import hash_block, hash_string256
from wallet import Wallet

MINING_REWARD = 10

class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        #initialising our empty blockchain list
        self.__chain = [genesis_block]
        #unhandled transactions
        self.__open_transactions = []
        self.hosting_node = hosting_node_id
        self.__peer_nodes = set()
        self.load_data()
         
    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transaction(self):
        return self.__open_transactions[:]

    def __iter__(self):
           return iter(self.__chain)

    def __getitem__(self, item):
         return self.__chain[item]       

    # blockchain = []    #list is used here
    # open_transactions = []          #list is used here
    # owner = 'Neel'              

    #function to load data from text files
    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                fileContent = f.readlines()
                
                """here [:-1] is used to neglect the '\n' at the end
                ...and json.loads is used to load data in python object format"""
                # if len(fileContent) == 0:
                #     return
                #to remove '/n' from the last
                blockchain = json.loads(fileContent[0][:-1])
                #to get the Ordered Dict back from the data just got read from file
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.__chain = updated_blockchain

                open_transactions = json.loads(fileContent[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'],tx['recipient'],tx['signature'],tx['amount'])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions 

                peer_nodes = json.loads(fileContent[2])
                self.__peer_nodes = set(peer_nodes)

        except (IOError, IndexError):
            print('Blockchain Record File not found !!')
        except ValueError:
            print('Value assignment error')
        except:
            print('Wild Card catcher for errors')
        finally:
            print('cleanUp after Loading execution (irrespective of done or not!)')    
    

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(savable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print('Saving failed')

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    # This function accepts two arguments.
    # One required one (transaction_amount) and one optional one (last_transaction)
    # The optional one has a default value => [1]


    def add_transaction(self,recipient, sender, signature, amount=1.0):
        """ Append a new value as well as the last blockchain value to the blockchain.

        Arguments:
            sender : sender of the coins
            recipient : reciever of the coins
            signature : signature of the Transaction
            amount : by default 1
        """
        # transaction = {
        #     'sender': sender,
        #     'recipient': recipient,
        #     'amount': amount
        # }
        if self.hosting_node == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        if(Verification.verify_transaction(transaction, self.get_balance)):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False    

    def mine_blocks(self):
        if self.hosting_node == None:
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # reward_transaction = {
        #     'sender' : 'MINING',
        #     'recipient' : owner,
        #     'amount' : MINING_REWARD    
        # }
        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD)
        #to copying by value not reference  
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            # print(tx.transaction)
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        #dictionary
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return block

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof+=1
        return proof

    def get_balance(self):
        if self.hosting_node == None:
            return None
        participant = self.hosting_node
        #list of amounts sent by a participant in blockchain
        tx_sender = [[tx.amount for tx in block.transactions
                    if tx.sender == participant] for block in self.__chain]
        #to get amount sent ... from open transactions that are not processed yet 
        # print(self.__open_transactions)
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]

        tx_sender.append(open_tx_sender)
        # print(participant)
        amount_sent = 0
        for tx in tx_sender:
            if len(tx) > 0:
                amount_sent+=sum(tx)
        # amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else 0, tx_sender)

        # print(tx_sender)
        tx_recipient = [[tx.amount for tx in block.transactions
                    if tx.recipient == participant] for block in self.__chain]    
        # print(tx_recipient)
        amount_recieved = 0
        # amount_recieved = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else 0, tx_recipient)

        for tx in tx_recipient:
            if len(tx) > 0:
                amount_recieved+=sum(tx)

        return amount_recieved  - amount_sent 

    def add_peer_node(self, node):
        """Adds a new node to the peer node set
            Arguments:
                node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Adds a new node to the peer node set
            Arguments:
                node: The node URL which should be removed.
        """
        self.__peer_nodes.discard(node)

    def get_peer_nodes(self):
        """returns the list of all peer nodes"""    
        return list(self.__peer_nodes)


