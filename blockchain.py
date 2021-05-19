'''
Author : Sankalp Narula
Date : 19-05-2021
Time: 12:56pm IST

'''
# importing the dependent libraries
import datetime
import hashlib
import json
from flask import Flask,jsonify

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