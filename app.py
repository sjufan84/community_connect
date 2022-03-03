import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import singleton_requests

load_dotenv()


#  Define and connect a new web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

# Once contract instance is loaded, build the Streamlit components and logic for interacting with the smart contract from the webpage
# Allow users to give pieces of information.  1-Select an account for the contract owner from a list of accounts.  2-Amount to donate

st.set_page_config(
    layout="wide",
    page_title = 'This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid',
    page_icon = 'Resources/CommunityConnect_image.png'
)

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


#st.header("""This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid""")
st.sidebar.title("Community Connect App")
#st.image('Resources/CommunityConnect_image.png', use_column_width='auto')

st.sidebar.title("Select a page")
page = st.sidebar.radio('', options=['Make a donation', 'Submit Request', 'View open requests', 'Request Cash Assistance', 'Send Remittance', 'Get Balances'])
st.sidebar.markdown("""---""")

# Dependending on which button is selected on the sidebar, the user will see a different ui and be able to interact with the contract
# in different ways

if page == 'Make a donation':

    st.header('Make a donation')

    # Create a streamlit 'form' that will allow for the batch submission to the smart contract
    # and then clear the data from the inputs
    
    with st.form("donation", clear_on_submit=True):
    
        accounts = w3.eth.accounts
        nonprofit = '0x6A11B707EcAE548501Ba9ab92a114C4b98378A08'
        address = st.multiselect('Select a Recipient', [nonprofit])
        donation = st.number_input("How much would you like to donate?")
        donation = int(donation)
        donor = '0x1A983C577B098b9C203D75cda21C984a365F93DB'

        submitted = st.form_submit_button("Donate")
        if submitted:
            tx_hash = contract.functions.deposit(donation).transact({
            'to': nonprofit,
            'from': donor,
            'value': donation
            })
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")
            dict_receipt = dict(receipt)
            st.write((dict_receipt))

            # calls receipt to add block
            singleton_requests.add_block(receipt)

            # Access the balance of an account using the address
            contract_balance = w3.eth.get_balance(nonprofit)
            # st.write(contract_balance)

            # Access information for the most recent block
            block_info = w3.eth.get_block("latest")
            # st.write(dict(block_info))


            # cc_df = pd.DataFrame.from_dict(dict_receipt)
            # st.write(cc_df)

if page == 'Submit Request':
    
    st.header('Submit a request')
    st.subheader('Please fill out request details below')

    with st.form("submitRequest", clear_on_submit=True):
        accounts = w3.eth.accounts
        owner_address = st.selectbox('Select address to submit request from', options = accounts)
        newName = st.text_input('What is the name of the product?')
        newProductType = st.selectbox('Select type of assistance requested', options = ['Food', 'Supplies', 'Ride'])
        
        # Input quantity of items requested if food or supplies, else ride quantity defaults to 1
        if newProductType != 'Ride':
            newProductCount = st.number_input('Enter product quantity requested')
        else:
            newProductCount = 1

        submitted = st.form_submit_button("Register Request")
        if submitted:
            tx_hash = contract.functions.registerRequest(
                owner_address,
                newName,
                newProductType,
                int(newProductCount)
            ).transact({'from' : owner_address})
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")
            st.write(dict(receipt))

if page == 'Request Cash Assistance':
    st.header('Submit a request for cash assistance')
    # sendRemittance function and streamlit
    with st.form("requestCash", clear_on_submit=True):
        accounts = w3.eth.accounts
        amount = st.number_input('Request for Cash Assistance')
        recipient = st.selectbox('Select a Recipient', options=accounts[5:10])  
        nonProfit = "0x6A11B707EcAE548501Ba9ab92a114C4b98378A08"
        
        submitted = st.form_submit_button("Request Cash Assistance")
        if submitted:
            tx_hash = contract.functions.sendRemittance(int(amount), recipient).transact({
                'from': nonProfit,
            })
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            st.write("Transaction receipt mined:")
            st.write(dict(receipt))

if page == 'Get Balances':
    st.header('Get Balances')
    # getBalance function and app.py

    with st.form("requestCash", clear_on_submit=True):
        accountowners = st.selectbox('Select account to Check Balance', options=accounts)
        submitted = st.form_submit_button("Get Balance")
        if submitted:
            tx_hash = w3.eth.get_balance(accountowners)
            wei = round(tx_hash,2) 
            eth = w3.fromWei(wei, "ether")
            st.write(f"This Account has a balance of {eth} Ether.")


if page == 'View open requests':
    
    st.header('Open Requests')
    #function viewRequest() view public returns(address, string memory, string memory, uint256) {
    #    return (accountOwner, name, productType, productCount);
    #}

   
    request = contract.functions.viewRequest().call()
    st.markdown(f'**Address of request:**   {request[0]}')
    st.markdown(f'**Name of item requested:**   {request[1]}')
    st.markdown(f'**Type of product:**   {request[2]}')
    st.markdown(f'**Quantity of product:**   {request[3]}')

    st.button('Offer to fill request')

    