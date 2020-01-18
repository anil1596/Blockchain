from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain
import json

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)

@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')

@app.route('/wallet', methods=['POST'])
def create_key():
    wallet.create_keys()
    if  wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key,
            'funds' : blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message' : 'Saving Keys failed',
            'wallet_set_up' : wallet.public_key != None
        } 
        return jsonify(response), 500

@app.route('/wallet', methods=['GET'])
def load_keys():
    if  wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key' : wallet.public_key,
            'private_key' : wallet.private_key,
            'funds' : blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message' : 'Loading Keys failed',
            'wallet_set_up' : wallet.public_key != None
        } 
        return jsonify(response), 500

@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message' : 'No Wallet Setup'
        }
        return jsonify(response), 400

    values = request.get_json()
    if not values:
        response = {
            'message' : 'No data Found'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message' : 'Required Data is missing'
        }
        return jsonify(response), 400
    signature = wallet.sign_transaction(wallet.public_key, values['recipient'], values['amount'])
    if not blockchain.add_transaction(values['recipient'], wallet.public_key, signature, values['amount']):
        response = {
            'message' : 'Add transaction Failed'
        }
        return jsonify(response), 400
    else:
        response = {
            'message' : 'Transaction Added Successfully',
            'transaction' :{
                'sender' : wallet.public_key,
                'recipient' : values['recipient'],
                'amount' : values['amount'],
                'signature' : signature
            },
            'funds' : blockchain.get_balance()
        }
        return jsonify(response), 201   

@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = blockchain.get_open_transaction()
    dict_transactions = [tx.__dict__.copy() for tx in transactions]
    # print(dict_transactions)
    response = {
        'message' : 'Fetched transactions successfully',
        'transactions' : dict_transactions
    }
    return jsonify(response), 201

@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            'message' : 'Fetched Balance Successfully',
            'funds' : balance
        }
        return jsonify(response), 201
    else: 
        response = {
            'message' : 'Get Balance failed',
            'wallet_set_up' : wallet.public_key != None
        } 
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__.copy() for tx in dict_block['transactions']]
    return jsonify(dict_chain), 201

@app.route('/mine', methods=['POST'])
def mine():
    block = blockchain.mine_blocks()
    if block != None:
        dict_block = block.__dict__.copy()
        # print('$$$' ,dict_block)
        dict_block['transactions'] = [tx.__dict__   for tx in dict_block['transactions']]
        response = {
            'message' : 'Block added Successfully',
            'block' : dict_block,
            'funds' : blockchain.get_balance()
        }    
        return jsonify(response), 201
    else:
        response = {
            'message' : 'Mining Failed',
            'wallet_set_up' : wallet.public_key != None
        } 
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5959)