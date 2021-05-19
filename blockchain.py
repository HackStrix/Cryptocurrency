'''
Author : Sankalp Narula
Date : 19-05-2021 Format (dd-mm-yyyy)
Time: 12:56pm IST

'''
# importing the dependent libraries
from flask import Flask, app,jsonify
import datetime
import hashlib
import json

# classes

class Blockchain():

    def __init__(self) -> None:
        self.chain = []
        self.create_block(proof = 1,previous_hash = '0')

    def create_block(self, proof, previous_hash):
        block = {
                "index":len(self.chain)+1,
                "timestamp":str(datetime.datetime.now()),
                "proof": proof,
                "previous_hash":previous_hash,
                "data": "This is sample data"
                }
        self.chain.append(block)
        return block

    def getpreviousblock(self):
        return self.chain[-1]

    def pow(self, previous_proof): # proof of work
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[0:5] == '00000':
                check_proof = True
            else:
                new_proof+=1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def isChainValid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[0:5] != '00000':
                return False
            previous_block = block
            block_index+=1
        return True








app = Flask(__name__)

blockchain_obj = Blockchain()

@app.route('/mineblock', methods=["GET"])

def mine_block():
    previous_block = blockchain_obj.getpreviousblock()
    previous_proof = previous_block['proof']
    proof = blockchain_obj.pow(previous_proof)
    previous_hash = blockchain_obj.hash(previous_block)
    block = blockchain_obj.create_block(proof, previous_hash)
    response = {
                'message': 'Congratulation, you just mined a block!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'previous_hash':block['previous_hash']
                }
    return jsonify(response), 200


# getting the full blockchain
@app.route('/getchain',methods = ['GET'])

def get_chain():
    response = {
                'chain': blockchain_obj.chain,
                'length': len(blockchain_obj.chain)
                }
    return jsonify(response), 200

@app.route('/isvalid', methods = ['GET'])
def is_valid():
    valid = blockchain_obj.isChainValid(blockchain_obj.chain)
    if valid:
        response = {'message':'All good BlockChain is valid'}
    else:
        response = {'message':'i think there is a problem'}
    return jsonify(response), 200
app.run(host='0.0.0.0',port=5000)