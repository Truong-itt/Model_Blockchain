from hashlib import sha256
import time
import json

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        # self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

class Blockchain:
    difficulty = 4

    def __init__(self):
        self.chain = []
        self.unconfirmed_transactions = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], 0, '0')
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def add_block(self, block, proof):
        print("Previous hash: ", block.previous_hash)
        print("Last block hash: ", self.last_block.hash)
        if block.previous_hash != self.last_block.hash:
            print("Invalid block")
            return False
        if not Blockchain.is_valid_proof(block, proof):
            print("Invalid proof")
            return False
        block.hash = proof
        self.chain.append(block)
        return self.last_block.index + 1


    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        new_block = Block(index=self.last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=self.last_block.hash)
        
        proof = self.proof_of_work(new_block)
        result = self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return result

    @classmethod
    def is_valid_proof(cls ,block, proof):
        print(block.__dict__)
        print("Block hash: ", block.compute_hash())
        print("Proof: ", proof)
        print(proof.startswith('0' * Blockchain.difficulty) and proof == block.compute_hash())
        return (proof.startswith('0' * Blockchain.difficulty) and proof == block.compute_hash())

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    @property
    def last_block(self):
        return self.chain[-1]
