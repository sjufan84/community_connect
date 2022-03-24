import datetime
import pandas as pd

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

# Display the information on the webpage
def update_block_chain_df(receipt, w3):
	# st.write("Transaction receipt mined:")
	dict_receipt = dict(receipt)
	contract_address = dict_receipt["to"]

	# Access the balance of an account using the address
	contract_balance = w3.eth.get_balance(contract_address)
	# st.write(contract_balance)

	# Access information for the most recent block
	block_info = w3.eth.get_block("latest")
	# st.write(dict(block_info))

	# calls receipt to add block
	add_block(receipt, contract_balance, block_info)

	block_chain = get_receipts()
	# st.write(block_chain)
	block_chain_df = pd.DataFrame.from_dict(block_chain)

	columns = ['Contract Balance', "Tx Hash", "From", "To", "Gas", "Timestamp"]
	block_chain_df.columns = columns
	block_chain_df.set_index('Tx Hash', inplace=True)
	block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

	return block_chain_df