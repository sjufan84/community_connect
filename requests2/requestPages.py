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
                try:
                    response = requests.get(url=f'https://api.mapbox.com/geocoding/v5/{endpoint}/{requestLocation}.json?access_token=pk.eyJ1Ijoic2p1ZmFuODQiLCJhIjoiY2wwYnBhencyMGxuMzNrbWkwZDBnNmV5MyJ9.03YEXe8EP_0JTE125vGCmA').json()
                    latitude = response['features'][0]['center'][1]
                    longitude = response['features'][0]['center'][0]
        
                    fig = go.Figure(go.Scattermapbox(lat=[latitude], lon=[longitude], 
                        mode='markers', marker=go.scattermapbox.Marker(size=18, symbol='car')))
        
                    fig.update_layout(hovermode='closest', title = f'{requestLocation}', mapbox=dict(
                        accesstoken=mapbox_access_token, bearing=0, center=go.layout.mapbox.Center(
                        lat=latitude, lon=longitude), pitch=0, zoom=15))
                except Exception:
                    pass
                
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
                singleton_functions.add_block(receipt, contract_balance, block_info)

                block_chain = singleton_functions.get_receipts()
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
                singleton_functions.add_block(receipt, contract_balance, block_info)

                block_chain = singleton_functions.get_receipts()
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
                singleton_functions.add_block(receipt, contract_balance, block_info)

                block_chain = singleton_functions.get_receipts()
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
                singleton_functions.add_block(receipt, contract_balance, block_info)

                block_chain = singleton_functions.get_receipts()
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
                singleton_functions.add_block(receipt, contract_balance, block_info)

                block_chain = singleton_functions.get_receipts()
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
                singleton_functions.add_block(receipt, contract_balance, block_info)

                block_chain = singleton_functions.get_receipts()
                # st.write(block_chain)
                block_chain_df = pd.DataFrame.from_dict(block_chain)

                columns = ['Contract Balance', "Tx Hash", "From", "To", "Gas", "Timestamp"]
                block_chain_df.columns = columns
                block_chain_df.set_index('Tx Hash', inplace=True)
                block_chain_df['Contract Balance'] = block_chain_df['Contract Balance'].astype('str')

                new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

                st.write(block_chain_df)

import streamlit as st
import pytz
import datetime as dt
from utils.contract import load_contract, get_provider
from patients.patientPages import page_addPatient
import pandas as pd
from pathlib import Path

contract = load_contract()
w3, node_provider = get_provider()
accounts = w3.eth.accounts

request_filter = contract.events.logNewRequest.createFilter(fromBlock='latest')

# Defining standard request column names and filtered column names
requests_df_columns = ["Patient Name", "PatientLocation", "Patient Neighborhood", "Preferred Language", "Needs Delivery", "Phone Number", "Is Quarantined", "Patient Id",
                "Provider", "Food Item Type", "Prep Considerations", "Baby Items", "Clothes Sizes", "Personal Care Type", "# of Adults", "# of Children", "Age and Gender of Children", 
                "Diaper Sizes", "Sleep Surface", "Other Special Items", "Other Notes", "Date Submitted", "Request Status"]
request_filters = ["Patient Name", "PatientLocation", "Patient Neighborhood", "Preferred Language", "Needs Delivery","Is Quarantined", "Patient Id",
                "Provider", "Food Item Type", "Prep Considerations", "Baby Items", "Clothes Sizes", "Personal Care Type", "# of Adults", "# of Children", "Age and Gender of Children", 
                "Diaper Sizes", "Sleep Surface", "Other Special Items", "Other Notes", "Date Submitted", "Request Status"]



# Defining format and inputs for requests pages
def page_newRequest():
    if 'requestPatientName' not in st.session_state:
        st.session_state.requestPatientName = ''
    if 'showPatient' not in st.session_state:
        st.session_state.showPatient = False
    
    patients_df = pd.read_csv(Path('./patients/patientsList.csv'), index_col=[0])
    patientNames = pd.Series()
    patientNames = patients_df.loc[:, "Patient Name"]
  
    st.header('New Request')

    st.subheader('Please fill out request details below')

    st.markdown('**If the patient you are requesting for has not been registered in the system, please click below to register them before submitting a goods request.**')
    amendPatient = st.button('Add New Patient')
    if amendPatient:
        page_addPatient()
   

    st.session_state.patientName = st.selectbox('Select Patient to Submit Request For:', options = patientNames.values)
    #usePatient = st.button("Make a Request for this Patient")
    #if usePatient:
     #   st.session_state.patientName = patientName
    
   
    with st.form("submitRequest", clear_on_submit=True):

        
        patientId = patients_df.loc[patients_df['Patient Name'] == st.session_state.patientName].index
        patientId = patientId[0]
        st.session_state.patientId = patientId
        patientInfo = pd.DataFrame(patients_df.loc[patientId]).astype(str)
        st.write(patientInfo)
        patientName = patientInfo.loc["Patient Name"].values[0]
        patientLocation = patientInfo.loc['Patient Location'].values[0]
        patientNeighborhood = patientInfo.loc['Patient Neighborhood'].values[0]
        preferredLanguage = patientInfo.loc['Preferred Language'].values[0]
        needsDelivery = patientInfo.loc['Needs Delivery'].values[0]
        is_quarintined = patientInfo.loc['Is Quarantined'].values[0]
        patientPhoneNumber = patientInfo.loc['Phone Number'].values[0]
        
        col1, col2 = st.columns(2)



        st.markdown("""---""")

        st.markdown('**If any of the above information is incorrect and needs to be updated, please click below to update patient information by selecting "Update Patient Information" on the left sidebar, otherwise continue the request below:**')
        #updateInfo = st.button("Update Patient Information", key='updateInfo')

        st.markdown("""---""")

        currentTime = dt.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')

        providerWallet = accounts[0]
        
        # Taking in requesters location to be mapped
        col1, col2 = st.columns(2)

        with col1:
            foodItemType = st.selectbox('What food items does the patient need?', options = ['Groceries (for families who can cook)',
                'No cook food bag (for families that do Not have access to a kitchen)',
                'No food items'])
            prepConsiderations = st.text_area('Any FOOD preparation considerations? (e.g. No access to kitchen or refridgeration)')
            numAdults = st.number_input('How many ADULTS live in the household? (this will help us pack appropriate amount of items)', value = 0)
            numChildren =  st.number_input('How many CHILDREN live in the household? (this will help us pack appropriate amount of items)', value=0)
            ageGenderChildren = st.text_area('Please list the age(s) and gender of the children in the household')
            otherPatientNotes = st.text_area('Anything else you would like us to know about this patient?')
            

        with col2:
            personalCareType = st.multiselect('What personal care item[s] does the patient need? (Hygiene Products)', options = [
                'Hand soap','Toothpaste/Toothbrushes', 'Pads', 'Other'
            ])
            otherCareTypes = st.text_input('If other, please specify', key='other1')
            personalCareType = f'{personalCareType}, {otherCareTypes}'
            sizeDiapers = st.multiselect('What size diaper[s] does the patient need?', options = [
                'Newborn','Size 1','Size 2','Size 3','Size 4','Size 5','Size 6','Pull-Ups 2T','Pull-ups 3T'
            ])
            babyItems = st.multiselect('What baby item[s] does the patient need?', options = [
                'Baby wipes', 'Baby cereal','Baby/kid girl clothes','Baby/kid boy clothes'
                'Newborn formula (Enfamil)','Newborn formula (Similac)'
            ])
            clothesSizes = st.text_area('If you are requesting clothes, what size?', value = 'e.g. 0-6m, 6-12m, 12-18m, 2T, 3T, etc.')
            sleepSurface = st.multiselect('What type of sleep surface does your patient need for their infant? Or any other special item[s]',
                options = ['Breastfeeding Pillow', 'Other'])
            otherSpecialItems = st.text_input('If other, please specify', key='other2')

        
        submitted = st.form_submit_button('submitRequest')
        if submitted:
            tx_hash = contract.functions.newRequest(
                accounts[0],
                int(patientId),
            ).transact({'from' : providerWallet})
            # Display the information on the webpage
            
            receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
            st.write(receipt)
            event = request_filter.get_new_entries()
            eventDict = dict(event[0]['args'])
            requestId = eventDict['requestId']
            st.markdown(f"Thank you!  Your addition of request **{requestId}** has been accepted.")
            thisRequests_df = pd.DataFrame(index = [requestId], columns = requests_df_columns).astype(str)
            thisRequests_df.loc[requestId] = {
            "Patient Name" : patientName,
            "PatientLocation" : patientLocation,
            "Patient Neighborhood" : patientNeighborhood,
            "Preferred Language" : preferredLanguage,
            "Needs Delivery" : needsDelivery,
            "Phone Number" : patientPhoneNumber,
            "Is Quarantined" : is_quarintined,
            "Patient Id" : st.session_state.patientId,
            "Provider" : providerWallet,
            "Food Item Type" : foodItemType,
            "Prep Considerations" : prepConsiderations,
            "Baby Items" : babyItems,
            "Clothes Sizes" : clothesSizes,
            "Personal Care Type" : personalCareType,
            "# of Adults" : numAdults,
            "# of Children" : numChildren,
            "Diaper Sizes" : sizeDiapers,
            "Sleep Surface" : sleepSurface,
            "Other Special Items" : otherSpecialItems,
            "Other Notes" : otherPatientNotes,
            "Date Submitted" : currentTime,
            "Age and Gender of Children" : ageGenderChildren,
            "Request Status" : "Open"
            }
            try:
                requests_df = pd.read_csv(Path('./requests2/requests.csv'), index_col = [0]).astype(str)
                requests_df = pd.concat([requests_df, thisRequests_df]).astype(str)
                requests_df.to_csv(Path('./requests2/requests.csv'))
            except Exception:
                requests_df = thisRequests_df.astype(str)
                requests_df.to_csv(Path('./requests2/requests.csv'))

            #requestId = contract.functions.getRequestCount.call()
            st.write(requestId)
            st.write(requests_df)

                

def page_viewRequests():
    st.session_state.page = "View Open Requests"
    st.header('Open Requests')
    try:
        requests_df = pd.read_csv(Path('./requests2/requests.csv'), index_col = [0]).astype(str)
        canViewRequests = True
    except:
        "There are no open requests to view right now"
        canViewRequests = False
        
    if canViewRequests == True:
        if "fillList" not in st.session_state:
            st.session_state.fillList = []
        st.markdown('**Click on column headers to sort dataframe by column values**')
        st.dataframe(requests_df)
        st.markdown(("""---"""))

        st.markdown('**If you  would like to generate a fill list, select the requests you would like to fill below:***')
        fillList = st.multiselect("Select request[s] to fill", options = requests_df.index)
        st.session_state.fillList = fillList
        fillList_df = pd.DataFrame(requests_df.loc[st.session_state.fillList]).astype(str)
        st.dataframe(fillList_df)
            
        with st.form('fillRequests', clear_on_submit=True):

            submitted = st.form_submit_button('Click here to save fill list and update requests dataframe requests statuses')
            
            if submitted:
                fillList_df.to_csv(Path('./requests2/fillList.csv'))
                requests_df.loc[st.session_state.fillList[['Request Status'] == "Open"], "Request Status"] = "Picked"         
                requests_df.to_csv(Path('./requests2/requests.csv'))
                st.markdown('**Fill List:**')
                st.dataframe(fillList_df)
                st.markdown('**Updated Requests List:**')
                st.dataframe(requests_df)