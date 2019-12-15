from functools import reduce
from collections import OrderedDict
from hash_util import hash_block, hash_string256
import json

MINING_REWARD = 10
# Initializing our (empty) blockchain list
genesis_block = {               #dictionary is used here
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
blockchain = [genesis_block]    #list is used here
open_transactions = []          #list is used here
owner = 'Neel'              
participants = {'Neel'}         #set is used here

#function to load data from text files
def load_data():
    with open('blockchain.txt', mode='r') as f:
        fileContent = f.readlines()
        global blockchain
        global open_transactions   
        """here [:-1] is used to neglect the '\n' at the end
           ...and json.loads is used to load data in python object format"""
        if len(fileContent) == 0:
            return

        blockchain = json.loads(fileContent[0][:-1])
        #to get the Ordered Dict back from the data just got read from file
        updated_blockchain = []
        for block in blockchain:
            updated_block = {
                'previous_hash': block['previous_hash'],
                'index': block['index'],
                'proof': block['proof'],
                'transactions': [OrderedDict(
                    [('sender',tx['sender']), ('recipient', tx['recipient']), ('amount',tx['amount'])]) for tx in block['transactions']]
            }
            updated_blockchain.append(updated_block)

        blockchain = updated_blockchain

        open_transactions = json.loads(fileContent[1])
        updated_transactions = []
        for tx in open_transactions:
            updated_transaction = [OrderedDict(
                    [('sender',tx['sender']), ('recipient', tx['recipient']), ('amount',tx['amount'])])]
            updated_transactions.append(updated_transaction)

        open_transactions = updated_transactions            

load_data()

def save_data():
    with open('blockchain.txt', mode='w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(open_transactions))

def get_last_blockchain_value():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

# This function accepts two arguments.
# One required one (transaction_amount) and one optional one (last_transaction)
# The optional one has a default value => [1]


def add_transaction(recipient, sender=owner,  amount=1.0):
    """ Append a new value as well as the last blockchain value to the blockchain.

    Arguments:
        sender : sender of the coins
        recipient : reciever of the coins
        amount : by default 1
    """
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if(verify_transaction(transaction)):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False    

def mine_blocks():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     'sender' : 'MINING',
    #     'recipient' : owner,
    #     'amount' : MINING_REWARD    
    # }
    reward_transaction = OrderedDict([('sender','MINING'), ('recipient', owner), ('amount',MINING_REWARD)])
    #to copying by value not reference  
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    #dictionary
    block = {              
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)
    return True

def valid_proof(transaction, last_hash, proof):
    guess = (str(transaction) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string256(guess)
    #print(guess_hash)
    return guess_hash[0:2] == '00'

def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof+=1
    return proof

def get_balance(participant):
    #list of amounts sent by a participant in blockchain
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    #to get amount sent ... from open transactions that are not processed yet 
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]

    tx_sender.append(open_tx_sender)
    print(participant)
    amount_sent = 0
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent+=sum(tx)
    # amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else 0, tx_sender)

    # print(tx_sender)
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]    
    # print(tx_recipient)
    amount_recieved = 0
    # amount_recieved = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else 0, tx_recipient)

    for tx in tx_recipient:
        if len(tx) > 0:
            amount_recieved+=sum(tx)

    return amount_recieved  - amount_sent 

def get_transaction_value():
    """ Returns the input of the user (a new transaction amount) as a float. """
    # Get the user input, transform it from a string to a float and store it in user_input
    tx_recipient = input('Enter the recipient of the transaction : ')
    tx_amount = float(input('Your transaction amount please : '))
    # returns a tuple
    return tx_recipient.strip(), tx_amount


def get_user_choice():
    user_input = input('Your choice : ')
    return user_input


def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputting Block')
        print(block)

def add_participant():
    participants.add(input('Enter the name of new participant : '))
    print(participants)

def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions ])

#to check whether the transaction can be performed or not
def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']

def verify_chain():
    """verify the current block and return True if the chain is valid one
       ... here enumerate extracts  INDEX and VALUE for list iterations"""
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index-1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            return False    
    return True


while True:
    print('\n Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new Block')
    print('3: Output the blockchain blocks')
    print('4: Add participant in blockchain')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()

    if user_choice == '1':
        tx_data = get_transaction_value()
        # destructring tuple
        recipient, amount = tx_data
        """Add transaction to the blockchain, here explicitely mentioning the 'amount = amount' 
           ...because amount is 3rd parameter in function definition"""
        if add_transaction(recipient, amount=amount):
            print('Transaction Successful')
        else: 
            print('Transaction Failed')    
        print(open_transactions)

    elif user_choice == '2':
        if mine_blocks():
            open_transactions = []
            save_data()

    elif user_choice == '3':
        print_blockchain_elements()

    elif user_choice == '4':
        add_participant()

    elif user_choice == '5':
        if verify_transactions():
            print('All Transactions are valid')
        else:
            print('Some Transactions are InValid')

    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{
                    'sender': 'anil',
                    'recipient': 'aman',
                    'amount': 10
                }]
            }

    elif user_choice == 'q':
        break

    else:
        print('Input was invalid, please pick a value from the list!')

    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break    

    print('Balance of {} : {:6.2f}'.format('Anil',get_balance('Anil')))

else:
    print('USER LEFT')

print('Done!')
