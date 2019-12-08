MINING_REWARD = 10
# Initializing our (empty) blockchain list
genesis_block = {               #dictionary is used here
    'previous_hash': '',
    'index': 0,
    'transaction': []
}
blockchain = [genesis_block]    #list is used here
open_transactions = []          #list is used here
owner = 'Neel'              
participants = {'Neel'}         #set is used here


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
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    if(verify_transaction(transaction)):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        return True
    return False    


def mine_blocks():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    reward_transaction = {
        'sender' : 'MINING',
        'recipient' : owner,
        'amount' : MINING_REWARD    
    }
    #to copying by value not reference  
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    #dictionary
    block = {              
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transaction': copied_transactions
    }
    blockchain.append(block)
    return True

def get_balance(participant):
    #list of amounts sent by a participant in blockchain
    tx_sender = [[tx['amount'] for tx in block['transaction'] if tx['sender'] == participant] for block in blockchain]
    #to get amount sent ... from open transactions that are not processed yet 
    open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = 0
    for tx in tx_sender:
        if len(tx) > 0:
            amount_sent += sum(tx)

    tx_recipient = [[tx['amount'] for tx in block['transaction'] if tx['recipient'] == participant] for block in blockchain]
    amount_recieved = 0
    print(tx_sender)
    print(tx_recipient)
    for tx in tx_recipient:
        if len(tx) > 0:
            amount_recieved += sum(tx)
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


def hash_block(last_block):
    #list comprehensions:  new_list = [key*2 for key in prvs_list]
    return '-'.join(str(last_block[key]) for key in last_block)


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
                'transaction': [{
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
    
    print('Balance of  :',get_balance('Anil'))
else:
    print('USER LEFT')

print('Done!')
