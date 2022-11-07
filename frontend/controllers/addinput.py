from controllers.config import input_contract


def tx_hash(hex_sql):
    th = input_contract.functions.addInput(hex_sql).transact()
    print("Transaction Hash:", th)
