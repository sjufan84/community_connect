import datetime
singleton = None

def convert_receipt(receipt, contract_balance, block_info):
    dict_receipt = dict(receipt)
    new_dict = {"contract_balance" : str(contract_balance)}
    receipt_include = ["transactionHash", "from", "to", "gasUsed"]
    block_include = ["timestamp"] ## convert timestamp
    # copy only key:value pairs from receipt_include into new_dict (for loop)
    for key in receipt_include:
        new_dict[key] = receipt[key]

    # copy only key, value pairs from block_include into new_dict (for loop)
    for key in block_include:
        new_dict[key] = block_info[key]

    # do timestamp conversion from line 7
    new_dict["timestamp"] = datetime.datetime.utcfromtimestamp(new_dict["timestamp"])
    new_dict["transactionHash"] = new_dict["transactionHash"].hex()

    return new_dict

def add_block(receipt, contract_balance, block_info):
    global singleton
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