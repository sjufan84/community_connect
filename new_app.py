import os
import json
from tkinter import N
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import singleton_requests
import yfinance as yf
import requests
from PIL import Image
import plotly.graph_objects as go

from ipfs import updateIPFS_df, retrieve_block_df

load_dotenv()

# Read in mapbox token for mapping
mapbox_access_token = os.getenv("MAPBOX_ACCESS_TOKEN")

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

# Function to convert USD to wei using yahoo finance api
def usdToWei(dollars):
    eth_df = yf.download(tickers="ETH-USD",period="today")
    eth_usd = eth_df.iloc[0]["Close"]
    to_ether = float(dollars) / float(eth_usd)
    to_wei = w3.toWei(to_ether, 'ether') 

    return to_wei

# Function converting wei to USD
def weiToUSD(wei):
    eth_df = yf.download(tickers="ETH-USD",period="today")
    eth_usd = eth_df.iloc[0]["Close"]
    st.write(eth_usd)
    ether = w3.fromWei(wei, 'ether')
    USD = float(ether) * float(eth_usd)
    
    return USD



#st.header("""This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid""")
st.sidebar.title("Community Connect App")
#st.image('Resources/CommunityConnect_image.png', use_column_width='auto')

st.sidebar.subheader("How Can We Help?")
page = st.sidebar.radio('', options=['Currency Converter', 'Make a Donation', 'Request for Goods', 'Request for Cash Assistance', 'Get Balances', 'View Contract Ledger'])
st.sidebar.markdown("""---""")

# Dependending on which button is selected on the sidebar, the user will see a different ui and be able to interact with the contract
# in different ways
block_chain_df = pd.DataFrame()

if page == 'Make a Donation':

    st.header('Make a Donation')

    # Create a streamlit 'form' that will allow for the batch submission to the smart contract
    # and then clear the data from the inputs
    
    with st.form("donation", clear_on_submit=True):
    
        accounts = w3.eth.accounts
      
        # For now we are just allowing donations to flow from the donor to the contract
        address = st.selectbox('Select a Recipient', options=[nonprofit])
        donation = st.number_input("How much would you like to donate?")
        choose_address = st.selectbox('Choose address to donate from', options = accounts[0:2])
        donation = int(donation)
        donation = usdToWei(donation)

        submitted = st.form_submit_button("Donate")
        if submitted:
            tx_hash = contract.functions.deposit(donation).transact({
            'from': choose_address,
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
            block_chain_df.set_index('Tx Hash', inplace=True)
            block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')
            
            # Utilizes the updateIPFS_df function from ipfs.py to concat running ledger
            # that lives on IPFS with the new block and then updates the new hash that is 
            # generated in the contract... this is repeated throughout the app script
            
            new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

            st.write(block_chain_df)
            st.balloons()


if page == 'Request for Goods':
    
    #st.subheader('Submit a Goods Request')
    goods_options = st.sidebar.radio('', options=['1 - Submit a Goods Request', '2 - View Open Goods Request', '3 - View Fill Goods Offers', '4 - Pay Supplier Invoice'])

    if goods_options == '1 - Submit a Goods Request':
        st.subheader('Please fill out request details below')
        #requestLocation = ''
        with st.form("submitRequest", clear_on_submit=True):

            # Taking in requesters location to be mapped
            col1, col2 = st.columns(2)
            with col1:
                street_address = st.text_input('Enter street address')
                state = st.text_input('Enter your state i.e. CA, AZ')
            with col2:
                city = st.text_input('Enter City')
                zip = st.text_input('Enter your zip code')

            col1, col2 = st.columns(2)
            
            with col1:
                newName = st.text_input('What is the name of the product?')
                newProductType = st.selectbox('Select type of assistance requested', options = ['Food', 'Supplies', 'Ride'])
            
            # Input quantity of items requested if food or supplies, else ride quantity defaults to 1
            with col2:
                owner_address = st.selectbox('Select your wallet address to submit request form', options = accounts[5:10])
                if newProductType != "Ride":
                    newProductCount = st.number_input('Enter product quantity requested', value=0)
                else:
                    newProductCount = 1

            submitted = st.form_submit_button("Register Request")
            if submitted:

                # Displays map of requesters location for confirmation
                requestLocation = f'{street_address} {city} {state} {zip}'
                endpoint = "mapbox.places" 
                response = requests.get(url=f'https://api.mapbox.com/geocoding/v5/{endpoint}/{requestLocation}.json?access_token=pk.eyJ1Ijoic2p1ZmFuODQiLCJhIjoiY2wwYnBhencyMGxuMzNrbWkwZDBnNmV5MyJ9.03YEXe8EP_0JTE125vGCmA').json()
                latitude = response['features'][0]['center'][1]
                longitude = response['features'][0]['center'][0]
        
                fig = go.Figure(go.Scattermapbox(lat=[latitude], lon=[longitude], 
                    mode='markers', marker=go.scattermapbox.Marker(size=18, symbol='car')))
        
                fig.update_layout(hovermode='closest', title = f'{requestLocation}', mapbox=dict(
                    accesstoken=mapbox_access_token, bearing=0, center=go.layout.mapbox.Center(
                    lat=latitude, lon=longitude), pitch=0, zoom=15))
               
                tx_hash = contract.functions.registerRequest(
                    owner_address,
                    newName,
                    newProductType,
                    int(newProductCount),
                    requestLocation
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
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

                st.markdown("**Thank you!  Your request is pending supplier confirmation!  Please confirm\
                your location below:**")
                #st.write(f'{requestLocation}')
                st.plotly_chart(fig, title=f'{requestLocation}')

                st.write(block_chain_df)

    # Supplier can view open supplies requests and offer to fill, optionally requesting
    # compensation to do so            
    if goods_options == '2 - View Open Goods Request':
        st.subheader('Supplier, please fill out form if you would like to fulfill this request')     
        with st.form('fillRequest', clear_on_submit=True):    

            request = contract.functions.viewRequest().call()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'**Requestor Wallet Address:**   {request[0]}')
                st.markdown(f'**Name of Item Requested:**   {request[1]}')
                st.markdown(f'**Type of Product:**   {request[2]}')
            with col2:
                st.markdown(f'**Quantity of Product:**   {request[3]}')
                st.markdown(f'**Request Location:**  {request[4]}')
                st.markdown(f'**Request Status:**  {request[5]}')
                
            st.markdown('### Supplier Information:')
            col1, col2, col3 = st.columns(3)
            with col1: 
                supplier= st.selectbox(f'Supplier Address', options=accounts[4:5])
            with col2:
                amount = st.number_input('Compensation requested')
                amount = usdToWei(amount)
            with col3:
                invoiceNumber = st.number_input('Invoice Number', value=0)
                
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
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

                # Pulling request data to be mapped
                request = contract.functions.viewRequest().call()
                requestLocation = f'{request[4]}'
                endpoint = "mapbox.places" 
                response = requests.get(url=f'https://api.mapbox.com/geocoding/v5/{endpoint}/{requestLocation}.json?access_token=pk.eyJ1Ijoic2p1ZmFuODQiLCJhIjoiY2wwYnBhencyMGxuMzNrbWkwZDBnNmV5MyJ9.03YEXe8EP_0JTE125vGCmA').json()
                latitude = response['features'][0]['center'][1]
                longitude = response['features'][0]['center'][0]
                fig = go.Figure(go.Scattermapbox(lat=[latitude], lon=[longitude],
                    mode='markers', marker=go.scattermapbox.Marker(size=18, symbol='car')))
        
                fig.update_layout(hovermode='closest', title = f'{request[4]}',
                    mapbox=dict(accesstoken=mapbox_access_token, bearing=0, center=go.layout.mapbox.Center(
                    lat=latitude, lon=longitude), pitch=0, zoom=15))

                st.markdown("#### Offer with Community Connect for Review & Approval")
                st.plotly_chart(fig, use_container_width=True)
                st.write(block_chain_df)
            

    if goods_options == '3 - View Fill Goods Offers':
        
        st.subheader("Community Connect, please review & approve supplier's offer to fulfill request")  
        with st.form('fillRequest', clear_on_submit=True):    

            # Allowing the suppliers to view open supplies requests and offer to fill
            request = contract.functions.viewFillOffer().call()
            supplier = accounts[4]
            compensationRequested = int(f'{request[1]}')
            compensationRequested = weiToUSD(compensationRequested)
            invoiceNumber = int(f'{request[2]}')
            st.markdown(f'**Supplier Address:**   {request[0]}')
            st.markdown(f'**Compensation Requested:**   {compensationRequested}')
            st.markdown(f'**InvoiceNumber:**   {request[2]}')
            st.markdown(f'**Product Name:**   {request[3]}')
            st.markdown(f'**Type of Product:**   {request[4]}')
            st.markdown(f'**Quantity of Product:**   {request[5]}')

            submitted = st.form_submit_button("Approve Offer")
            if submitted:
                tx_hash = contract.functions.approveFillOffer().transact({
                    'from': nonprofit,
                })
                
                # Display the information on the webpage
                receipt = w3.eth.waitForTransactionReceipt(tx_hash)
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
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)
                
                st.write(block_chain_df)
                st.write("Great! This order will be prepped and sent to requestor!")


    if goods_options == '4 - Pay Supplier Invoice':
        
        st.subheader('Goods Received and Invoice Approved to be Paid to Supplier')
        with st.form("payInvoice", clear_on_submit=True):

            # Once the fill offer has been approved, the nonprofit will be able
            # to pay the supplier via the contract balance
            request = contract.functions.viewApprovedInvoice().call()
            compensationApproved = int(f'{request[1]}')
            compensationApproved = weiToUSD(compensationApproved)
            
            invoiceNum = int(f'{request[2]}')
            st.markdown(f'**Approved Supplier Address:**   {request[0]}')
            st.markdown(f'**Approved Compensation:**   {compensationApproved}')
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
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

                st.write(block_chain_df)
                st.write(f"Good News! Request submission for **Invoice {invoiceNum}** has been received from requestor and invoice paid to supplier!")
                st.balloons()


if page == 'Request for Cash Assistance':

    st.header('Request for Cash Assistance')
    cash_options = st.sidebar.radio('', options=['1 - Submit Request for Cash', '2 - Review Cash Request'])

    # Authorized recipient can make a request for cash below
    if cash_options == '1 - Submit Request for Cash':
        with st.form("cash request", clear_on_submit=True):

            recipient = st.selectbox('Provide Your Public Address', options=accounts[5:6])  # Currently only first hash listed is the only authorizedRecipient in our smart contract
            amount = st.number_input('Provide Amount Needed')
            amount = int(amount)
            amount = usdToWei(amount)
            address = st.selectbox('Your request will be fulfilled by:', [nonprofit])

            submitted = st.form_submit_button("Request for Cash Assistance")
            if submitted:
                tx_hash = contract.functions.requestCash(recipient, amount).transact({
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
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

                st.write(block_chain_df)

    # Non-profit can view open cash requests and approve or deny... if approved
    # the cash is immediately deployed to the recipient
    if cash_options == '2 - Review Cash Request':
        
        st.subheader("Open Cash Request Sent for Approval")
        with st.form("viewCashInvoice", clear_on_submit=True):

            request = contract.functions.viewCashRequest().call()
            cashRequested = int(f'{request[1]}')
            cashRequested = weiToUSD(cashRequested)
            st.markdown(f'**Requestor Address:**   {request[0]}')
            st.markdown(f'**Amount Requested:**   {cashRequested}')
            st.markdown(f'**Cash request status:** {request[2]}')
            
            submitted = st.form_submit_button("Approve Cash Request")
            if submitted:
                tx_hash = contract.functions.sendCash(request[1], request[0], nonprofit).transact({
                    'from': nonprofit,
                })

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
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

                st.write(block_chain_df)

if page == 'Get Balances':
    st.header('Get Balances')
    # getBalance function and app.py

    with st.form("viewBalances", clear_on_submit=True):
        # Here we allow the user to view any account balance in the contract with a selectbox
        # and display it in wei, ether, and USD
        accountowners = st.selectbox('Select account to Check Balance', options=accounts)
        submitted = st.form_submit_button("Get Balance")
        if submitted:
            tx_hash = w3.eth.get_balance(accountowners)
            wei = round(tx_hash,2) 
            eth = w3.fromWei(wei, "ether")
            eth_df = yf.download(tickers="ETH-USD",period="today")
            eth_usd = eth_df.iloc[0]["Close"]
            usd_balance = float(eth_usd)*float(eth)
            st.write(f"This account has a balance of **{tx_hash:,.2f} WEI:**")

            st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")

    # Here we incorporate graphics to illustrate the movement of money between accounts
    # preselected as supplier, donor, recipient and contract
    col1, col2 = st.columns(2)
    with col1:
        st.image(Image.open(Path('./Resources/Donor.png')))
        donor_balance = w3.eth.get_balance(accounts[0])
        wei = round(donor_balance,2) 
        eth = w3.fromWei(wei, "ether")
        eth_df = yf.download(tickers="ETH-USD",period="today")
        eth_usd = eth_df.iloc[0]["Close"]
        usd_balance = int(eth_usd)*int(eth)
        st.write(f"This account has a balance of **{donor_balance:,.2f} WEI:**")
        st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")

        st.image(Image.open(Path('./Resources/Contract.png')))
        contractBalance = w3.eth.get_balance(contract.address)
        wei = round(contractBalance,2) 
        eth = w3.fromWei(wei, "ether")
        eth_df = yf.download(tickers="ETH-USD",period="today")
        eth_usd = eth_df.iloc[0]["Close"]
        usd_balance = float(eth_usd)*float(eth)
        st.write(f"This account has a balance of **{contractBalance:,.2f} WEI:**")
        st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")

    with col2:
        st.image(Image.open(Path('./Resources/Recipient.png')))
        recipientBalance = w3.eth.get_balance(accounts[5])
        wei = round(recipientBalance,2) 
        eth = w3.fromWei(wei, "ether")
        eth_df = yf.download(tickers="ETH-USD",period="today")
        eth_usd = eth_df.iloc[0]["Close"]
        usd_balance = float(eth_usd)*float(eth)
        st.write(f"This account has a balance of **{recipientBalance:,.2f} WEI:**")
        st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")

        st.image(Image.open(Path('./Resources/Supplier.png')))
        supplierBalance = w3.eth.get_balance(accounts[4])
        wei = round(supplierBalance,2) 
        eth = w3.fromWei(wei, "ether")
        eth_df = yf.download(tickers="ETH-USD",period="today")
        eth_usd = eth_df.iloc[0]["Close"]
        usd_balance = float(eth_usd)*float(eth)
        st.write(f"This account has a balance of **{supplierBalance:,.2f} WEI:**")
        st.write(f"**{eth:,.2f} ETHER** or **${usd_balance:,.2f} USD**.")
             

# Page that allows user to view the current contract ledger pulled from ipfs
if page == 'View Contract Ledger':

    st.header('Contract Ledger')

    ipfsHash = contract.functions.getIPFSHash().call()
    if ipfsHash == '':
        st.write('No transactions to display yet')
    else:
        totalIPFS_df = retrieve_block_df(ipfsHash)
        st.write(totalIPFS_df)
    

# Basic currency converter to allow the user to convert between USD, ether and wei
if page == 'Currency Converter':
    with st.form('converter', clear_on_submit = True):
        st.header('Currency Converter')

        eth_df = yf.download(tickers="ETH-USD",period="today")
        eth_usd = eth_df.iloc[0]["Close"]
        dollars = st.number_input('Enter the amount of USD to convert to ether and wei:', value = 0.00)
        to_ether = float(dollars) / float(eth_usd)
        to_wei = w3.toWei(to_ether, 'ether')

        submitted = st.form_submit_button('Convert')
        if submitted:
            st.markdown(f'**{dollars} dollars is equal to {to_ether:,.2f} ether**')
            st.markdown(f'**{dollars} dollars is equal to {to_wei:,.2f} wei**')

   