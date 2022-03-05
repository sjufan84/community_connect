import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import singleton_requests
import yfinance as yf

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

st.sidebar.title("Select a Page")
page = st.sidebar.radio('', options=['Make a Donation', 'Submit Request', 'View Open Requests', 'Request for Cash Assistance', 'Send Remittance', 'Get Balances'])
st.sidebar.markdown("""---""")

# Dependending on which button is selected on the sidebar, the user will see a different ui and be able to interact with the contract
# in different ways

if page == 'Make a Donation':

    st.header('Make a Donation')

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
            # st.write("Transaction receipt mined:")
            dict_receipt = dict(receipt)
            # st.write((dict_receipt))

            # Access the balance of an account using the address
            contract_balance = w3.eth.get_balance(nonprofit)
            # st.write(contract_balance)

            # Access information for the most recent block
            block_info = w3.eth.get_block("latest")
            # st.write(dict(block_info))

            # calls receipt to add block
            singleton_requests.add_block(receipt, contract_balance, block_info)

            block_chain = singleton_requests.get_receipts()
            # st.write(block_chain)
            block_chain_df = pd.DataFrame.from_dict(block_chain)

            columns = ['Contract Balance', "Tx Hash", "From", "To", "Gas", "Timestamp"]
            block_chain_df.columns = columns

            st.write(block_chain_df)


if page == 'Submit a Request':
    
    st.header('Submit a Request')
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

if page == 'Request for Cash Assistance':
    st.header('Request for Cash Assistance')
    # sendRemittance function and streamlit
    with st.form("requestCash", clear_on_submit=True):
        accounts = w3.eth.accounts
        recipient = st.selectbox('Provide Your Public Address', options=accounts[5:10])  # Currently only first hash listed is the only authorizedRecipient in our smart contract
        amount = st.number_input('Provide Amount Needed')
        amount = int(amount)
        nonprofit = "0x6A11B707EcAE548501Ba9ab92a114C4b98378A08"
        address = st.multiselect('Your request will be fulfilled by:', [nonprofit])

        submitted = st.form_submit_button("Request for Cash Assistance")
        if submitted:
            tx_hash = contract.functions.sendRemittance(amount, recipient, nonprofit).transact({
                'from': nonprofit,
            })
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            # st.write("Transaction receipt mined:")
            dict_receipt = dict(receipt)
            # st.write((dict_receipt))

            # Access the balance of an account using the address
            contract_balance = w3.eth.get_balance(nonprofit)
            # st.write(contract_balance)

            # Access information for the most recent block
            block_info = w3.eth.get_block("latest")
            # st.write(dict(block_info))

            # calls receipt to add block
            singleton_requests.add_block(receipt, contract_balance, block_info)

            block_chain = singleton_requests.get_receipts()
            # st.write(block_chain)
            block_chain_df = pd.DataFrame.from_dict(block_chain)

            columns = ['Contract Balance', "Tx Hash", "From", "To", "Gas", "Timestamp"]
            block_chain_df.columns = columns

            st.write(block_chain_df)

if page == 'Get Balances':
    st.header('Get Balances')
    # getBalance function and app.py

    with st.form("requestCash", clear_on_submit=True):
        accounts = w3.eth.accounts
        accountowners = st.selectbox('Select account to Check Balance', options=accounts)
        submitted = st.form_submit_button("Get Balance")
        if submitted:
            tx_hash = w3.eth.get_balance(accountowners)
            wei = round(tx_hash,2) 
            eth = w3.fromWei(wei, "ether")
            eth_df = yf.download(tickers="ETH-USD",period="today" )
            eth_usd = eth_df.iloc[0]["Close"]
            usd_balance = int(eth_usd)*int(eth)
            st.write(f"This Account has a balance of {eth} Ether or {usd_balance}$.")


if page == 'View Open Requests':
    
    st.header('Open Requests')
    #function viewRequest() view public returns(address, string memory, string memory, uint256) {
    #    return (accountOwner, name, productType, productCount);
    #}

    request = contract.functions.viewRequest().call()
    st.markdown(f'**Address of request:**   {request[0]}')
    st.markdown(f'**Name of item requested:**   {request[1]}')
    st.markdown(f'**Type of product:**   {request[2]}')
    st.markdown(f'**Quantity of product:**   {request[3]}')

    
    
        #supplier_private_key = '4deb3c6a476ac1f674b83d5ec1834122d7cceaae3395ddaf5f193f8bc585cd8e'
        #nonce = w3.eth.get_transaction_count(supplier_address, 'latest' )
        #payload={'from': supplier_address, 'nonce': nonce}
        
        #create another input asking for compensation requested
        #raw_fill_txn = contract.functions.fillRequest().buildTransaction(payload)
        #signed_txn = w3.eth.account.signTransaction(raw_fill_txn, private_key=supplier_private_key)
        #fill_tx = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        #tx_hash= contract.functions.fillRequest().call()
        #receipt = w3.eth.waitForTransactionReceipt(fill_tx)
        #st.write("Transaction receipt mined:")
        #st.write(dict(receipt))
        
    with st.form('fillRequest', clear_on_submit=True):    
        accounts = w3.eth.accounts
        supplier_address = '0x2c8e3e5EC4064612d4936970dc27e2d930f78245'
        st.subheader('If you would like to fill this request, please fill out the form below:')    
        supplier= st.selectbox(f'Supplier Address', options=accounts[4:5])
        amount = st.number_input('Compensation requested')
        invoiceNumber = st.number_input('Invoice Number')
        st.header('Send Invoice')
        #supplier = st.text_input('Name')
        #type = st.text_input('Type')
        supplier_private_key = '4deb3c6a476ac1f674b83d5ec1834122d7cceaae3395ddaf5f193f8bc585cd8e'
        nonce = w3.eth.get_transaction_count(supplier, 'latest' )
        payload={'from': supplier, 'nonce': nonce, "gasPrice": w3.eth.gas_price}
        submit = st.form_submit_button("Send Invoice")
        if submit:
        #supplier = '0x2c8e3e5EC4064612d4936970dc27e2d930f78245'
            approve_tx = contract.functions.fillRequest(
                supplier,
                int(amount),
                int(invoiceNumber)
            ).buildTransaction(payload)
            sign_tx = w3.eth.account.signTransaction(approve_tx, supplier_private_key)
            tx_hash_1 = w3.eth.sendRawTransaction(sign_tx.rawTransaction)
            
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash_1)
            st.write("Transaction receipt mined:")
            dict_receipt = dict(receipt)
            st.write((dict_receipt))
                
                
        
    #invoice_number = st.number_input('Invoice Number')
    


    fill = st.button('Offer to fill request')
    if fill:
        accounts = w3.eth.accounts
        supplier_address = '0x2c8e3e5EC4064612d4936970dc27e2d930f78245'
        supplier_private_key = '4deb3c6a476ac1f674b83d5ec1834122d7cceaae3395ddaf5f193f8bc585cd8e'
        nonce = w3.eth.get_transaction_count(supplier_address, 'latest' )
        payload={'from': supplier_address, 'nonce': nonce}
        
        #create another input asking for compensation requested
        raw_fill_txn = contract.functions.fillRequest().buildTransaction(payload)
        signed_txn = w3.eth.account.signTransaction(raw_fill_txn, private_key=supplier_private_key)
        fill_tx = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        #tx_hash= contract.functions.fillRequest().call()
        receipt = w3.eth.waitForTransactionReceipt(fill_tx)
        st.write("Transaction receipt mined:")
        st.write(dict(receipt))
        
            
        st.subheader('Please fill out request for Compensation')
        with st.form("sendInvoice"):
            supplier= st.selectbox(f'Supplier Address', options=accounts[4:5])
            #supplier = st.text_input('Name')
            #type = st.text_input('Type')
            amount = st.number_input('Quantity')
            invoiceNumber = st.number_input('Invoice Number')
            st.header('Send Invoice')
            submit= st.form_submit_button("Send Invoice")
           
            if submit:
                accounts = w3.eth.accounts
                #supplier_address = '0x2c8e3e5EC4064612d4936970dc27e2d930f78245'
                supplier_private_key = '4deb3c6a476ac1f674b83d5ec1834122d7cceaae3395ddaf5f193f8bc585cd8e'
                nonce = w3.eth.get_transaction_count(supplier, 'latest' )
                payload={'from': supplier, 'nonce': nonce}
                
                approve_tx = contract.functions.sendInvoice(
                    supplier,
                    int(amount),
                    int(invoiceNumber)
                    
                    
                ).buildTransaction(payload)
                sign_tx = w3.eth.account.signTransaction(approve_tx, private_key=supplier_private_key)
                tx_hash_1 = w3.eth.sendRawTransaction(sign_tx.rawTransaction)
                # Display the information on the webpage
                receipt = w3.eth.waitForTransactionReceipt(tx_hash_1)
                st.write("Transaction receipt mined:")
                st.write(dict(receipt))
            
        #invoice_number = st.number_input('Invoice Number')
    

