singleton = None

def convert_receipt(receipt, contract_balance, block_info):
    dict_receipt = dict(receipt)
    new_dict = {"contract_balance" : contract_balance}
    receipt_include = ["transactionHash", "from", "to", "gasUsed"]
    block_include = ["timestamp"] # convert timestamp
    # copy only key:value pairs from receipt_include into new_dict (for loop)
    for key, value in receipt_include.items():
        new_dict[key].insert(0, value)
    # copy only key:value pairs from block_include into new_dict (for loop)
    for key, value in block_include.items():
        new_dict[key].insert(0, value)
    return new_dict

def add_block(receipt, contract_balance, block_info):
    dict_receipt = convert_receipt(receipt, contract_balance, block_info)
    if not singleton:
        singleton = {}
        for key in dict_receipt.keys():
            singleton[key] = []
    for key, value in dict_receipt.items():
        singleton[key].insert(0, value)
    return singleton

def get_receipts():
    if not singleton:
        return "There are no receipts to display."
    return singleton