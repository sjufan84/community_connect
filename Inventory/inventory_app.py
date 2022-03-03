import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import datetime as dt
import streamlit as st

load_dotenv()

st.caption("""This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid""")
st.sidebar.title("Community Connect App")
#  Define and connect a new web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Cache the contract to tell Streamlit to load this contract only one time, regardless of other changes
@st.cache(allow_output_mutation=True)
def load_contract():
    # Load the contract's ABI details
    with open(Path('product_abi.json')) as f:
        product_abi = json.load(f)

    # Contract function next needs to read the address of the deployed contract from the .env file.
    contract_address = '0x279BFDdB38c74b6b16d87C1f3c519fc6883d8A8c'

    # Connect to the contract
    contract = w3.eth.contract(
        address = contract_address,
        abi = product_abi
    )
    return contract


contract = load_contract()

# Once contract instance is loaded, build the Streamlit components and logic for interacting with the smart contract from the webpage
# Allow users to give pieces of information.  1-Select an account for the contract owner from a list of accounts.  2-Amount to donate

accounts = w3.eth.accounts
owner_address = st.selectbox('Select an address to register a product from', options=accounts)
product_name = st.text_input('What is the name of the product you want to add?')
productType = st.selectbox(label = 'Product Type', options = ['Diapers', 'Food'])
productCost = st.number_input('Enter the cost of the product')
productLocation = st.text_input('What is the location (address) of the product?')
productCount = st.number_input('What is the quantity of items you are adding?')
uploadDate = '11/21/2022'
TokenURI = st.text_input('Input product URI')


if st.button("Add product"):
    tx_hash = contract.functions.registerProduct(
        product_name,
        productType,
        int(productCost),
        productLocation,
        int(productCount),
        uploadDate,
        TokenURI
    ).transact({'from' : owner_address})
    # Display the information on the webpage
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

    
    

#st.sidebar.write("Make a Donation")
#community_connect = '0x6A11B707EcAE548501Ba9ab92a114C4b98378A08'
#if st.button("Make a Donation"):
#    tx_hash = contract.functions.deposit(donation).transact({
#        'to': address,
#        'from':donor,
#        'value':donation 
#    })
#    