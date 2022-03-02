import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

load_dotenv()

st.caption("""This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid""")
st.sidebar.title("Community Connect App")
#  Define and connect a new web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Cache the contract to tell Streamlit to load this contract only one time, regardless of other changes
@st.cache(allow_output_mutation=True)
def load_contract():
    # Load the contract's ABI details
    with open(Path('./contracts/compiled/CC_abi.json')) as f:
        CC_abi = json.load(f)

    # Contract function next needs to read the address of the deployed contract from the .env file.
    contract_address = os.getenv("SMART_CONTRACT_ADDRESS")

    # Connect to the contract
    contract = w3.eth.contract(
        address = contract_address,
        abi = CC_abi
    )
    return contract


contract = load_contract()

# Once contract instance is loaded, build the Streamlit components and logic for interacting with the smart contract from the webpage
# Allow users to give pieces of information.  1-Select an account for the contract owner from a list of accounts.  2-Amount to donate

accounts = w3.eth.accounts
address = st.multiselect('Select a Recipient', options=accounts)
donation = st.number_input("How much would you like to donate?")
nonProfit = '0x6A11B707EcAE548501Ba9ab92a114C4b98378A08'

donation = int(donation)
donor = "0x1A983C577B098b9C203D75cda21C984a365F93DB"

if st.button("Make a Donation"):
    tx_hash = contract.functions.deposit(donation).transact({
        'to': '0x6A11B707EcAE548501Ba9ab92a114C4b98378A08',
        'from': '0x1A983C577B098b9C203D75cda21C984a365F93DB',
        'value': donation
    })
    # Display the information on the webpage
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))
    #receipt_df = pd.read_json(receipt)

    # Access the balance of an account using the address
    contract_balance = w3.eth.get_balance(nonProfit)
    st.write(contract_balance)

    # Access information for the most recent block
    block_info = w3.eth.get_block("latest")
    st.write(dict(block_info))

    # List of accounts on the blockchain
    # st.write(w3.eth.accounts)

#st.sidebar.write("Make a Donation")
#community_connect = '0x6A11B707EcAE548501Ba9ab92a114C4b98378A08'
#if st.button("Make a Donation"):
#    tx_hash = contract.functions.deposit(donation).transact({
#        'to': address,
#        'from':donor,
#        'value':donation 
#    })

# Create an empty DataFrame for all transactions
# cc_df = pd.DataFrame()