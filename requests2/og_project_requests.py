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

