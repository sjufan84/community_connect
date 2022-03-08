import os
import json
from tkinter import N
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import singleton_requests
#import ipfs
import yfinance as yf

from ipfs import convert_df_to_json, pin_json_to_ipfs, retrieve_block_df

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

# list of accounts
accounts = w3.eth.accounts
nonprofit = accounts[3]
supplier_address = accounts[4]
supplier_key = os.getenv("SUPPLIER_PRIVATE_KEY")
nonprofit_key = os.getenv('NONPROFIT_PRIVATE_KEY')
donor = accounts[0]


#st.header("""This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid""")
st.sidebar.title("Community Connect App")
#st.image('Resources/CommunityConnect_image.png', use_column_width='auto')

st.sidebar.subheader("How Can We Help?")
page = st.sidebar.radio('', options=['Make a Donation', 'Request for Goods', 'Request for Cash Assistance', 'Get Balances'])
st.sidebar.markdown("""---""")

#['Make a Donation', 'Submit a Request', 'View Open Request', 'Pay Invoice', 'Request for Cash Assistance', 'Get Balances', 'View Fill Offers']

# Dependending on which button is selected on the sidebar, the user will see a different ui and be able to interact with the contract
# in different ways
block_chain_df = pd.DataFrame()

if page == 'Make a Donation':

    st.header('Make a Donation')

    # Create a streamlit 'form' that will allow for the batch submission to the smart contract
    # and then clear the data from the inputs
    
    with st.form("donation", clear_on_submit=True):
    
        accounts = w3.eth.accounts
      
        address = st.selectbox('Select a Recipient', options=[nonprofit])
        donation = st.number_input("How much would you like to donate?")
        donation = int(donation)

        submitted = st.form_submit_button("Donate")
        if submitted:
            tx_hash = contract.functions.deposit(donation).transact({
            'from': donor,
            'value': donation
            })
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            # st.write("Transaction receipt mined:")
            dict_receipt = dict(receipt)
            # st.write((dict_receipt))
            contract_address = dict_receipt["to"]

            # Access the balance of an account using the address
            contract_balance = w3.eth.get_balance(contract_address)
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

            block_json_df = convert_df_to_json(block_chain_df)
            ipfs_hash = pin_json_to_ipfs(block_json_df)
            tx_hash2 = contract.functions.updateIPFSHash(ipfs_hash).transact({
                'from' : donor
            })
            #returned_block_df = retrieve_block_df(ipfs_hash)

            st.write(block_chain_df, ipfs_hash)
            st.balloons()
            #st.write(block_json_df, ipfs_hash, returned_block_df)

#ipfs_hash = pin_json_to_ipfs(block_json_df)
#block_df = retrieve_block_df(ipfs_hash)

if page == 'Request for Goods':
    
    goods_options = st.sidebar.radio('', options=['Submit a Goods Request', 'View Open Goods Request', 'View Fill Goods Offers', 'Pay Supplier Invoice'])

    if goods_options == 'Submit a Goods Request':
        st.header('Submit a goods request below')
        with st.form("submitRequest", clear_on_submit=True):
            owner_address = st.selectbox('Select your address to submit request form', options = accounts[5:10])
            newName = st.text_input('What is the name of the product?')
            newProductType = st.selectbox('Select type of assistance requested', options = ['Food', 'Supplies', 'Ride'])
            
            # Input quantity of items requested if food or supplies, else ride quantity defaults to 1
            if newProductType != "Ride":
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

                dict_receipt = dict(receipt)
                contract_address = dict_receipt["to"]

                # Access the balance of an account using the address
                contract_balance = w3.eth.get_balance(contract_address)
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

    if goods_options == 'View Open Goods Request':
        
        st.header('View Open Goods Request')
            
        with st.form('fillRequest', clear_on_submit=True):    

            request = contract.functions.viewRequest().call()
            st.markdown(f'**Requestor Address:**   {request[0]}')
            st.markdown(f'**Name of Item Requested:**   {request[1]}')
            st.markdown(f'**Type of Product:**   {request[2]}')
            st.markdown(f'**Quantity of Product:**   {request[3]}')
            st.markdown(f'**Request Status:**  {request[4]}')

            st.subheader('Supplier, please fill out form if you would like to fulfill this request')    
            supplier= st.selectbox(f'Supplier Address', [supplier_address])
            amount = st.number_input('Compensation requested')
            invoiceNumber = st.number_input('Invoice Number', value=0)

            #supplier = st.text_input('Name')
            #type = st.text_input('Type')
            nonce = w3.eth.get_transaction_count(supplier, 'latest')
            payload={'from': supplier, 'nonce': nonce, "gasPrice": w3.eth.gas_price}
            submitted = st.form_submit_button("Send Offer")
            if submitted:
                approve_tx = contract.functions.fillRequest(
                    supplier,
                    int(amount),
                    int(invoiceNumber)
                ).buildTransaction(payload)
                sign_tx = w3.eth.account.signTransaction(approve_tx, supplier_key)
                tx_hash_1 = w3.eth.sendRawTransaction(sign_tx.rawTransaction)
                
                # Display the information on the webpage
                receipt = w3.eth.waitForTransactionReceipt(tx_hash_1)
                dict_receipt = dict(receipt)
                contract_address = dict_receipt["to"]
                # st.write((dict_receipt))

                # Access the balance of an account using the address
                contract_balance = w3.eth.get_balance(contract_address)
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
                    
                st.subheader("Offer with Community Connect for Approval")

    if goods_options == 'View Fill Goods Offers':
        
        st.header('View Fill Goods Offers')
            
        with st.form('fillRequest', clear_on_submit=True):    

            request = contract.functions.viewFillOffer().call()
            supplier = accounts[4]
            compensationRequested = int(f'{request[1]}')
            invoiceNumber = int(f'{request[2]}')
            st.markdown(f'**Supplier Address:**   {request[0]}')
            st.markdown(f'**Compensation Requested:**   {request[1]}')
            st.markdown(f'**InvoiceNumber:**   {request[2]}')
            st.markdown(f'**Product Name:**   {request[3]}')
            st.markdown(f'**Type of Product:**   {request[4]}')
            st.markdown(f'**Quantity of Product:**   {request[5]}')

            nonce = w3.eth.get_transaction_count(nonprofit, 'latest')
            payload={'from': nonprofit, 'nonce': nonce, "gasPrice": w3.eth.gas_price}
            submitted = st.form_submit_button("Approve Offer")
            if submitted:
                approve_tx = contract.functions.approveFillOffer(
                ).buildTransaction(payload)
                sign_tx = w3.eth.account.signTransaction(approve_tx, nonprofit_key)
                tx_hash_1 = w3.eth.sendRawTransaction(sign_tx.rawTransaction)
                
                # Display the information on the webpage
                receipt = w3.eth.waitForTransactionReceipt(tx_hash_1)
                dict_receipt = dict(receipt)
                contract_address = dict_receipt["to"]
                # st.write((dict_receipt))

                # Access the balance of an account using the address
                contract_balance = w3.eth.get_balance(contract_address)
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


    if goods_options == 'Pay Supplier Invoice':
        
        st.header('Pay Supplier Invoice')
        st.subheader('Confirm below goods have been received and invoice is approved to be paid')

        with st.form("payInvoice", clear_on_submit=True):

            request = contract.functions.viewApprovedInvoice().call()
            
            
            invoiceNum = int(f'{request[2]}')
            st.markdown(f'**Approved Supplier Address:**   {request[0]}')
            st.markdown(f'**Approved Compensation:**   {request[1]}')
            st.markdown(f'**Approved Invoice Number:**   {request[2]}')
            
            submitted = st.form_submit_button("Pay Invoice")
            if submitted:
                tx_hash = contract.functions.payInvoice(
                    invoiceNum=invoiceNum,
                    received=True
                ).transact({'from' : nonprofit})
                # Display the information on the webpage
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)

                dict_receipt = dict(receipt)
                contract_address = dict_receipt["to"]

                # Access the balance of an account using the address
                contract_balance = w3.eth.get_balance(contract_address)
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
                    
                #st.subheader("Offer with Community Connect for Approval")

if page == 'Pay Invoice':
    
    st.header('Pay Invoice')
    st.subheader('Confirm below goods have been received and invoice is approved to be paid')

    with st.form("payInvoice", clear_on_submit=True):

        request = contract.functions.viewApprovedInvoice().call()
        
        
        invoiceNum = int(f'{request[2]}')
        st.markdown(f'**Approved Supplier Address:**   {request[0]}')
        st.markdown(f'**Approved Compensation:**   {request[1]}')
        st.markdown(f'**Approved Invoice Number:**   {request[2]}')
        
        submitted = st.form_submit_button("Pay Invoice")
        if submitted:
            tx_hash = contract.functions.payInvoice(
                invoiceNum=invoiceNum,
                received=True
            ).transact({'from' : nonprofit})
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)

            dict_receipt = dict(receipt)
            contract_address = dict_receipt["to"]

            # Access the balance of an account using the address
            contract_balance = w3.eth.get_balance(contract_address)
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
                
            #st.subheader("Offer with Community Connect for Approval")

if page == 'Request for Cash Assistance':
    st.header('Request for Cash Assistance')

    st.sidebar.radio('', options=['Submit Request for Cash', 'View Cash Request', 'Approve Cash Request'])

    with st.form("cash request", clear_on_submit=True):

        recipient = st.selectbox('Provide Your Public Address', options=accounts[5:10])  # Currently only first hash listed is the only authorizedRecipient in our smart contract
        amount = st.number_input('Provide Amount Needed')
        int_amount = int(amount)
        address = st.multiselect('Your request will be fulfilled by:', [nonprofit])

        submitted = st.form_submit_button("Request for Cash Assistance")
        if submitted:
            tx_hash = contract.functions.requestCash(int_amount, recipient, nonprofit).transact({
                'from': nonprofit,
            })
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
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
            singleton_requests.add_block(receipt, contract_balance, block_info)

            block_chain = singleton_requests.get_receipts()
            # st.write(block_chain)
            block_chain_df = pd.DataFrame.from_dict(block_chain)

            columns = ['Contract Balance', "Tx Hash", "From", "To", "Gas", "Timestamp"]
            block_chain_df.columns = columns

            st.write(block_chain_df)

            st.subheader("Request with Community Connect for Approval")
            submit = st.form_submit_button("Approve Request")
            if submit:
                nonprofit_approved = contract.functions.sendCash(int_amount, recipient, nonprofit).transact({
                'from': nonprofit,
                })
                # Display the information on the webpage
                receipt = w3.eth.waitForTransactionReceipt(nonprofit_approved)
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
        accountowners = st.selectbox('Select account to Check Balance', options=accounts)
        submitted = st.form_submit_button("Get Balance")
        if submitted:
            tx_hash = w3.eth.get_balance(accountowners)
            wei = round(tx_hash,2) 
            eth = w3.fromWei(wei, "ether")
            eth_df = yf.download(tickers="ETH-USD",period="today")
            eth_usd = eth_df.iloc[0]["Close"]
            usd_balance = int(eth_usd)*int(eth)
            st.write(f"This account has a balance of **{tx_hash:,.2f} WEI:**")

            st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")
             
if page == 'View Fill Offers':
    
    st.header('Open Fill Offers')
        
    with st.form('fillRequest', clear_on_submit=True):    

        request = contract.functions.viewFillOffer().call()
        supplier = accounts[4]
        compensationRequested = int(f'{request[1]}')
        invoiceNumber = int(f'{request[2]}')
        st.markdown(f'**Supplier Address:**   {request[0]}')
        st.markdown(f'**Compensation Requested:**   {request[1]}')
        st.markdown(f'**InvoiceNumber:**   {request[2]}')
        st.markdown(f'**Product Name:**   {request[3]}')
        st.markdown(f'**Type of Product:**   {request[4]}')
        st.markdown(f'**Quantity of Product:**   {request[5]}')

        nonce = w3.eth.get_transaction_count(nonprofit, 'latest')
        payload={'from': nonprofit, 'nonce': nonce, "gasPrice": w3.eth.gas_price}
        submitted = st.form_submit_button("Approve Offer")
        if submitted:
            approve_tx = contract.functions.approveFillOffer(
            ).buildTransaction(payload)
            sign_tx = w3.eth.account.signTransaction(approve_tx, nonprofit_key)
            tx_hash_1 = w3.eth.sendRawTransaction(sign_tx.rawTransaction)
            
            # Display the information on the webpage
            receipt = w3.eth.waitForTransactionReceipt(tx_hash_1)
            dict_receipt = dict(receipt)
            contract_address = dict_receipt["to"]
            # st.write((dict_receipt))

            # Access the balance of an account using the address
            contract_balance = w3.eth.get_balance(contract_address)
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

            st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")

