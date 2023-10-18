from sys import argv
from web3 import Web3
from solcx import compile_source, install_solc

install_solc("0.7.0")

# Config Web3
w3 = Web3(Web3.HTTPProvider('https://ropsten.infura.io/v3/aa6cf3979cd74049b1be941bce8a8b34'))
# Private key account ethereum
private_key = "893c5b14df07bb36d3ef297d33eb604e9c46fa35079313db25f6f6434b80c1df"
# Sign
acct = w3.eth.account.privateKeyToAccount(private_key)
# Pool
proposition = ["Coca-Cola", "Pepsi", "Sprite"]

def compile_source_file(file):
    with open(file, 'r') as f:
      source = f.read()

    return compile_source(source)

def deploy_contract(proposition):
    # Deploy contract in Infura
    
    print("Contract start deploy !")
    
    compiled_sol = compile_source_file('Voting.sol')
    contract_interface = compiled_sol['<stdin>:Voting']
    
    Voting = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    
    tx_hash = Voting.constructor(proposition).buildTransaction({'from' : acct.address, 'nonce' : w3.eth.getTransactionCount(acct.address)})
    
    signed = acct.signTransaction(tx_hash)
    
    transact = w3.eth.send_raw_transaction(signed.rawTransaction)
    
    tx_receipt = w3.eth.waitForTransactionReceipt(transact)
    
    print("Contract end deploy !")
    
    return tx_receipt, contract_interface

def receive_contract(address_contract, abi):
    return w3.eth.contract(address=address_contract, abi=abi)

def vote(id, contract):
    
    print("Vote in progress...")
    
    address_vote = contract.functions.chairperson().call()
    tx_vote = contract.functions.vote(id).buildTransaction({'from' : address_vote, 'nonce' : w3.eth.getTransactionCount(address_vote)})
    signed_vote = acct.signTransaction(tx_vote)
    transact_vote = w3.eth.send_raw_transaction(signed_vote.rawTransaction)
        
    w3.eth.waitForTransactionReceipt(transact_vote)
    
    print("You are voting !")

def main(argv):
    
    (receipe, contract_interface) = deploy_contract(proposition)
    
    contract = receive_contract(receipe.contractAddress, contract_interface['abi'])
    
    vote(0, contract)
    vote(1, contract)
    vote(2, contract)
    vote(0, contract)
    
    print("Winner is : ", contract.functions.winnerName().call())
    
if __name__ == "__main__":
    main(*argv)