'''
Author : Sankalp Narula
Date : 21-05-2021 Format (dd-mm-yyyy)
Time: 11:45pm IST

'''
# importing the dependent libraries

import datetime
import requests
from flask import request,Flask,app,jsonify 
import hashlib
import json
from uuid import uuid4
from urllib.parse import urlparse

from werkzeug.wrappers import response


class Blockchain():

    def __init__(self) -> None:
        self.mempool = []
        self.chain = []
        self.create_block(proof = 1,previous_hash = '0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
                "index":len(self.chain)+1,
                "timestamp":str(datetime.datetime.now()),
                "proof": proof,
                "previous_hash":previous_hash,
                "transactions": self.mempool
                }
        self.mempool = []
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

    def add_transaction(self,sender,receiver, amount):
        self.mempool.append({
                            'sender':sender,
                            'receiver':receiver,
                            'amount':amount
                            })
        return self.getpreviousblock()['index'] + 1
    
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get((f'http://{node}/getchain'))
            if response.status_code == 200:
                if response.json()['length'] > max_length and self.isChainValid(response.json()['chain']):
                    max_length = response.json()['length']
                    longest_chain = response.json()['chain']
                else:
                    pass
            else: 
                print("the node is offline")
        if longest_chain:
            self.chain = longest_chain
            return True
        return False




app = Flask(__name__)
# creating an address for node 5000
node_address = str(uuid4()).replace('-','')

blockchain_obj = Blockchain()

@app.route('/mineblock', methods=["GET"])

def mine_block():
    previous_block = blockchain_obj.getpreviousblock()
    previous_proof = previous_block['proof']
    proof = blockchain_obj.pow(previous_proof)
    blockchain_obj.add_transaction(node_address,'Sankalp',5)
    previous_hash = blockchain_obj.hash(previous_block)
    block = blockchain_obj.create_block(proof, previous_hash)
    response = {
                'message': 'Congratulation, you just mined a block!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'transactions':block['transactions'],
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


@app.route('/addtransaction',methods = ['GET','POST'])
def add_transaction():
    json_content = request.get_json()
    # print(json_content)
    transaction_keys=['sender','receiver','amount']
    # if not all (key in json_content for key in transaction_keys):
    #     return "Some keys are missing",400
    index = blockchain_obj.add_transaction(json_content['sender'],json_content['receiver'],json_content['amount'])
    return f'Transaction successfull, block {index} will be mined shortly', 201

# Decentralizing the network

#connecting new nodes
@app.route('/connectnode',methods = ['POST'])
def connect_node():
    json_content = request.get_json()
    nodes = json_content.get('nodes')
    if nodes is None:
        return "no node", 400
    # blockchain_obj.add_node(json_content["address"])
    for node in nodes:
        blockchain_obj.add_node(node)
    response = {
                "message":"All the nodes are now connected",
                "all the nodes:" :list(blockchain_obj.nodes)
                }
    return jsonify(response),201


@app.route('/replacechain', methods = ['GET'])
def replace_chain():
    is_replaced = blockchain_obj.replace_chain()
    if is_replaced:
        response = {
                    'message':'All good BlockChain now is replaced',
                    'new_chain':blockchain_obj.chain
                    }
    else:
        response = {
                    'message':'i think were good',
                    'actual_chain': blockchain_obj.chain
                    }
    return jsonify(response), 200


app.run(host='0.0.0.0',port=5000)

