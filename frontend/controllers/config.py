import json
from web3 import Web3

def getAddress():
    adress_file = open("../deployments/localhost/dapp.address",'r')
    rollups_address = adress_file.read()
    return rollups_address
    
def getABI():
    input_abi_file = open("../deployments/localhost/InputFacet.json",'r')
    input_abi_json = json.load(input_abi_file)
    input_abi = input_abi_json["abi"]
    input_abi = json.dumps(input_abi)
    return input_abi

def getContract():
    address = getAddress()
    abi = getABI()
    web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    input_contract = web3.eth.contract(abi=abi, address=address)
    return input_contract
    
