# Distributed ledger using Blockchain
 It keep tracks of the transactions happening in-between the users in the peer network and user gets rewarded for the each of the new block being mined. Transations are being tracked using  public key of the sender and recipient, implemented using [RSA](https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html). 

## How the things look on the browser
1: 

## Show me how to run this thing!

1: Clone the directory
 `git clone git@github.com:anil1596/Blockchain.git`
 
2: Run the python script on system(s)
 `python3 node.py -p {MENTION PORT NUMBER}`
 
3: Go to `http://0.0.0.0:{PORT NUMBER}/` in browser

## Directory Structure

1: `/chains` : folder to store the Blockchain data for the current user (it's being stored in text format to understand it better).

2: `/ui` : folder to store the User Interface components. 

3: `/utility` : directory to stores the utility classes/module of the project. 
      
    
        ├── hash_util.py : used to get the hashed value of a block using hashlib.sha256
        ├── printable.py : inherited to other classes to print objects.
        ├── verification.py : used to perform following verification checks :
        ├    ├── to verify valid Proof of Work (here first 2 digits of hash must be 00)
        ├    ├── verify whole blockchain by comparing previous_hash of current block and calculated hash of previous block.
        ├    ├── verify a particular transaction by checking balance of the sender 
        ├    ├── verifying all open transactions.
   
4: `/wallet` : used to store the public/private key of the user.

5: `block.py` : Blueprint of a block in blockchain, which consists of index, previous_hash, transactions, proof of work (nonce), timestamp of the block creation.

6: `blockchain.py` : Blueprint of the blockchain consists of various attributes and methods.

        ├── __init__ : constructor of the blockchain
        ├    ├── genesis_block : initial block in the blockchain.
        ├    ├── chain : actual blockchain the user is having/working upon.
        ├    ├── public_key : User identifier
        ├    ├── peer_nodes : list of the nodes in the network.
        ├    ├── resolve_conflicts : flag to check if the current blockchain is not valid then get the latest blockchain.
        ├    ├── load_data() : to get the initial data/blockchain/open_transactions while loading.
        ├    ├── save_data(): function to store the data on successful mining/transaction.
        ├    ├── mine_block(): function to mine a (new block + rewarding user) and broadcasting the updated blockchain to the all peers.
        ├    ├── add_block(): function to update the local blockchain upon receiving updated chain from peers in the network.
        ├    ├── proof_of_work() : function to calculate proof of work number for a new block.
        ├    ├── get_balance() : function to get the remaining funds of the user after transaction.
        ├    ├── add_peer_node()/remove_peer_node : functions to add/remove peer node.
        ├    ├── resolve() : function to resolve conflicts in the transactions and calculating the winner chain.
    
7: `node.py` : 
    > to make a server/client handle of the user using [Flask](https://flask.palletsprojects.com/en/1.1.x/). 
    > works as main() of the project and consists of all the routes to a server/client using GET/POST methods.          

8: `transaction.py` : Blueprint of the transaction, consists of the sender, recipient, amount, digital signature.

9: `wallet.py` : used to create user identifier using public keys.
    
    ├─ create_keys() : function to create public key using RSA.generate(
    ├─ load_keys() :  function to load already existing keys.
    ├─ save_keys() : function to save newly created user identifier.
    ├─ sign_transaction() : to sign the user transaction using sender, receiver, amount information.
    ├─ verify_transaction() : to validate any particular transaction in the blockchain.

10: `reset.sh` : shell script to erase all the locally stored data in one go using `./reset.sh` from terminal.
    
    
