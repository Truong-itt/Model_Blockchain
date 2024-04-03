from flask import Flask, request, jsonify
from blockchain_operators import Block, Blockchain
import time
import json
import requests

app = Flask(__name__)
blockchain = Blockchain()
peers = set()
blockchain.create_genesis_block()

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data,
        "peers": list(peers)})

@app.route('/new_transaction', methods=['POST'])
def add_new_transaction():
    tx_data = request.get_json()
    required_fields = ['title', 'author']
    if not all(field in tx_data for field in required_fields):
        return 'Invalid transaction data', 400
    tx_data['timestamp'] = time.time()
    blockchain.new_transaction(tx_data)
    return 'Transaction added successfully', 201

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transaction():
    result = blockchain.mine()
    if not result:
        return 'No transactions to mine', 200
    else:
        chain_length = len(blockchain.chain)
        get_consensus()
        if chain_length == len(blockchain.chain):
            annouce_new_block(blockchain.last_block)
        return "block #{} is mined.".format(blockchain.last_block.index), 200

@app.route('/register_node', methods=['POST'])
def register_new_node():
    node_address = request.get_json().get('node_address')
    if not node_address:
        return 'Invalid data', 400
    peers.add(node_address)
    return get_chain()

@app.route('/register_node_with', methods=['POST'])
def register_node_with():
    node_address = request.get_json().get('node_address')
    if not node_address:
        return 'Invalid data', 400
    data = {'node_address': request.host_url}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(node_address + '/register_node', data=json.dumps(data), headers=headers)
    if response.status_code == 200:
        global blockchain
        global peers
        chain_dump = response.json()['chain']
        blockchain = create_change_from_chaindump(chain_dump)
        peers.update(response.json()['peers'])
        return 'Registration successful and chain synchronized', 200
    return response.content, response.status_code

@app.route("/add_block", methods=['POST'])
def add_block():
    block_data = request.get_json()
    block = Block(index=block_data["index"], 
                transactions=block_data["transactions"],
                timestamp=block_data["timestamp"], 
                previous_hash=block_data["previous_hash"],
                nonce=block_data["nonce"])
    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    if not added:
        return "The block was discarded by the node", 400
    return "Block added to the chain", 201

def create_change_from_chaindump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    
    genesis_hash = generated_blockchain.chain[0].hash  # Lấy hash của khối genesis hiện tại

    for idx, block_data in enumerate(chain_dump):
        if idx == 0: continue  # Bỏ qua khối genesis trong chain dump
        block = Block(index=block_data["index"], 
                      transactions=block_data["transactions"],
                      timestamp=block_data["timestamp"], 
                      previous_hash=block_data["previous_hash"],
                      nonce=block_data["nonce"])
        proof = block_data["hash"]
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("Failed to add block from chain dump. The chain dump might be tampered!")
    return generated_blockchain

def get_consensus():
    global blockchain
    longest_chain = None
    current_length = len(blockchain.chain)
    
    # brower chain in url
    for node in peers:
        response = requests.get("{}/chain".format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_length:
            current_length = length
            longest_chain = chain
    if longest_chain:
        blockchain = longest_chain
        return True
    return False

def annouce_new_block(block):
    # lay link add vao he thong 
    for node in peers:
        url = "{}add_block".format(node) 
        headers = {'Content-Type': 'application/json'}
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True), headers=headers)

    


 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
