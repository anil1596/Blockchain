#file to get all the user inputs
from blockchain import Blockchain
from uuid import uuid4
from verification import Verification

class Node():
    def __init__(self):
        self.id = str(uuid4())
        self.blockchain = Blockchain(self.id)

    def get_user_choice(self):
        user_input = input('Your choice : ')
        return user_input

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction amount) as a float. """
        # Get the user input, transform it from a string to a float and store it in user_input
        tx_recipient = input('Enter the recipient of the transaction : ')
        tx_amount = float(input('Your transaction amount please : '))
        # returns a tuple
        return tx_recipient.strip(), tx_amount

    def print_blockchain_elements(self):
        # Output the blockchain list to the console
        for block in self.blockchain.get_chain():
            print('Outputting Block')
            print(block)
        else:
            print('-'*20)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new Block')
            print('3: Output the blockchain blocks')
            print('h: Manipulate the chain')
            print('q: Quit')
            user_choice = self.get_user_choice()

            if user_choice == '1':
                tx_data = self.get_transaction_value()
                # destructring tuple
                recipient, amount = tx_data
                """Add transaction to the blockchain, here explicitely mentioning the 'amount = amount' 
                ...because amount is 3rd parameter in function definition"""
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Transaction Successful')
                else: 
                    print('Transaction Failed')    
                print(self.blockchain.get_open_transaction())

            elif user_choice == '2':
                 self.blockchain.mine_blocks()

            elif user_choice == '3':
                self.print_blockchain_elements()

            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transaction, self.blockchain.get_balance):
                    print('All Transactions are valid')
                else:
                    print('Some Transactions are InValid')

            elif user_choice == 'h':
                if len(self.blockchain) >= 1:
                    self.blockchain.get_chain()[0] = {
                        'previous_hash': '',
                        'index': 0,
                        'transactions': [{
                            'sender': 'anil',
                            'recipient': 'aman',
                            'amount': 10
                        }]
                    }

            elif user_choice == 'q':
                waiting_for_input = False

            else:
                print('Input was invalid, please pick a value from the list!')
            if not Verification.verify_chain(self.blockchain):
                self.print_blockchain_elements()
                print('Invalid Blockchain')
            # if not verify_chain():
            #     print_blockchain_elements()
            #     print('Invalid blockchain!')
            #     break    

            print('Balance of {} : {:6.2f}'.format(self.id, self.blockchain.get_balance()))

        else:
            print('USER LEFT')

        print('Done!')

node = Node()
node.listen_for_input()