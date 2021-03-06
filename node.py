from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain
import json

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def get_node_ui():
    return send_from_directory('ui', 'node.html')

@app.route('/network', methods=['GET'])
def get_network_ui():
    return send_from_directory('ui', 'network.html')

@app.route('/wallet', methods=['POST'])
def create_key():
    wallet.create_keys()
    if  wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
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
        blockchain = Blockchain(wallet.public_key, port)
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

@app.route('/broadcast-transaction', methods=['POST'])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            'message' : 'No data Found'
        }
        return jsonify(response), 400
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(key in values for key in required):
        response = {
            'message' : 'Some data missing'
        }
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values['recipient'], values['sender'], values['signature'], values['amount'], is_receiving=True)
    if success:
        response = {
            'message' : 'Transaction Added Successfully',
            'transaction' :{
                'sender' : values['sender'],
                'recipient' : values['recipient'],
                'amount' : values['amount'],
                'signature' : values['signature']
            }
        }
        return jsonify(response), 201 
    else :
        response = {
            'message' : 'Creating a Transaction Failed'
        }
        return jsonify(response), 500

@app.route('/broadcast-block', methods=['POST'])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            'message' : 'No Block data Found'
        }
        return jsonify(response), 400
    if 'block' not in values:
        response = {
            'message' : 'Some Data is missing'
        }
        return jsonify(response), 400
    block = values['block']
    if block['index'] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {
                'message' : 'Block Added Successfully'
            }
            return jsonify(response), 201
        else:
            response = {
                'message' : 'Block Seems Invalid'
            }
            return jsonify(response), 409

    elif block['index'] > blockchain.chain[-1].index:
        #local blockchain needs to be updated
        response = {
            'message' : 'Blockchain seems different from LOCAL Blockchain'
        }
        blockchain.resolve_conflicts = True 
        return jsonify(response), 200
    elif block['index'] < blockchain.chain[-1].index:
        print('Blockchain Seems to be shorter one!!')
        response = {
            'message' : 'Blockchain seems to be shorter one'
        }
        return jsonify(response), 409

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
    #to check if any conflict aroused while mining the block
    if blockchain.resolve_conflicts :
        response = {
                 'message':'Need to resolve Conflicts, Block cannot be added'
            }
        return jsonify(response), 409  
    if block != None:
        dict_block = block.__dict__.copy()
        # print('$$$' ,dict_block)
        dict_block['transactions'] = [tx.__dict__   for tx in dict_block['transactions']]
        response = {
            'message' : 'Block Mined Successfully',
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

@app.route('/node', methods=['POST'])
def add_node():
    values = request.get_json()
    print(values)
    if not values:
        response = {
            'message' : 'No data attached'
        }
        return jsonify(response), 400
    if 'node' not in values:
        response = {
            'message' : 'No node data found'
        }
        return jsonify(response), 400
    node = values['node']
    blockchain.add_peer_node(node)
    response = {
            'message' : 'Node added Successfully',
            'all_nodes' : blockchain.get_peer_nodes()
        }
    return jsonify(response), 201   

@app.route('/node/<node_url>', methods=['DELETE'])
def remove_node(node_url):
    if node_url == '' or node_url == None:
        response = {
            'message' : 'No node data attached',
            'all_nodes' : blockchain.get_peer_nodes()
        }
        return jsonify(response), 400 
    blockchain.remove_peer_node(node_url)
    response = {
        'message' : 'Node Removed',
        'all_nodes' : blockchain.get_peer_nodes()
    }
    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
        'all_nodes' : blockchain.get_peer_nodes()
    }
    return jsonify(response), 200

@app.route('/resolve-conflicts', methods=['POST'])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {
            'message' : 'Chain was updated'
        }
    else :
        response = {
            'message' : 'Local Chain kept'
        }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default = 5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key, port)
    app.run(host='0.0.0.0', port=port)