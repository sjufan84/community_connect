from operator import index
from turtle import update
import streamlit as st
from utils.contract import load_contract, get_provider
import pandas as pd
from pathlib import Path

contract = load_contract()
w3, node_provider = get_provider()
accounts = w3.eth.accounts

provider_df_columns = ["Provider Wallet Address", "Provider's Name", "Clinic Name", "Contact Name", "Contact Phone #", "Provider Location", "Provider Email"]


def page_addProvider():
    st.session_state.page = "Add Provider"
    
    st.header('Add a provider below:')
    with st.form('addProvider', clear_on_submit=True):
        col1, col2 = st.columns(2)
       
        with col1:
            user_address = accounts[0]
            providerName = st.text_input("Provider's Name")
            clinicName = st.text_input("Name of provider's clinic")
            providerEmail = st.text_input("Provider's Email Address")
            contactName = st.text_input("Provider's Contact Name")
            contactPhoneNumber = st.text_input("Provider's Contact Phone #")
        with col2:
            providerWallet = st.selectbox('Provider Wallet Address', options = [accounts[0]])
            street_address = st.text_input('Enter provider street address')
            city = st.text_input('Enter Provider City')
            state = st.text_input('Enter Provider State i.e. CA, AZ')
            zip = st.text_input('Enter Provider Zip Code')
            providerLocation = f'{street_address} {city} {state} {zip}'

        submitted = st.form_submit_button('Add Provider')
        if submitted:
            tx_hash = contract.functions.addProvider(
                providerName,
                providerWallet,
                clinicName            
                ).transact({'from' : user_address})
            # Display the information on the webpage
            receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
            st.write(receipt)

            
            newProviderId = contract.functions.getProviderId().call()
            newProvider_df = pd.DataFrame(index=[newProviderId], columns = provider_df_columns)
            newProvider_df.loc[newProviderId] = {
                "Provider Wallet Address" : providerWallet, 
                "Provider's Name" : providerName, 
                "Clinic Name" : clinicName, 
                "Contact Name" : contactName, 
                "Contact Phone #" : contactPhoneNumber, 
                "Provider Location" : providerLocation, 
                "Provider Email" : providerEmail
            }
            
            try:
                providers_df = pd.read_csv(Path('./providers/providerList.csv'), index_col = [0]).astype(str)
                newProvider_df = newProvider_df.astype(str)
                providers_df = pd.concat([providers_df, newProvider_df])
                providers_df.to_csv('./providers/providerList.csv')
            except:
                providers_df = newProvider_df.astype(str)
                providers_df.to_csv('./providers/providerList.csv')

            st.write(providers_df)

            


def page_updateProvider():

    st.header('Update Provider Info')
    if 'updateProviderName' not in st.session_state:
        st.session_state.updateProviderName = ''
    if 'updateProviderUser' not in st.session_state:
        st.session_state.updateProviderUser = ''

    try:
        updateProvider_df = pd.read_csv(Path('./providers/providerList.csv'), index_col = [0]).astype(str)
        updateProvider_df.index = updateProvider_df.index.astype(str)
        providerNames = pd.Series()
        providerNames = updateProvider_df["Provider's Name"].values
    except:
        st.markdown("#### No providers to update")

    with st.form('selectProviderUpdate', clear_on_submit=True):
        st.subheader('Current Provider List')
        st.write(updateProvider_df)
        updateProviderName = st.selectbox("Select Name of Provider You Wish to Update", options = providerNames)
        submitted = st.form_submit_button(f'Update Info')
        if submitted:
            st.session_state.updateProviderName = updateProviderName
            st.experimental_rerun()

    providerInfo = pd.Series()
    providerInfo = updateProvider_df.loc[updateProvider_df["Provider's Name"] == st.session_state.updateProviderName]
    providerId = updateProvider_df.loc[updateProvider_df["Provider's Name"] == st.session_state.updateProviderName].index
    st.write(providerInfo)
    providerColumns = pd.Series()
    providerColumns = providerInfo.columns


    st.markdown('**Please select the column[s] you would like to edit:**')

    updateSelections = st.multiselect('', options = providerColumns.values)



    col1, col2 = st.columns(2)
    if updateSelections != '':
        for selection in updateSelections:
            with col1:
                if selection == "Provider's Name":
                    providerName = st.text_input("Provider's Updated Name")
                    updateProvider_df.loc[providerId, "Provider's Name"] = providerName
                elif selection == "Clinic Name":
                    clinicName = st.text_input("Updated Clinic Name")
                    updateProvider_df.loc[providerId, "Clinic Name"] = clinicName
                elif selection == "Contact Name":
                    contactName = st.text_input('Updated Contact Name')
                    updateProvider_df.loc[providerId, "Contact Name"] = contactName
            with col2:
                if selection == "Contact Phone #":
                    contactNumber = st.text_input("Updated Contact Phone #")
                    updateProvider_df.loc[providerId, "Contact Phone #"] = contactNumber
                elif selection == "Provider Location":
                    st.markdown(f"**Enter new provider location:**")
                    street_address = st.text_input('Enter provider street address')
                    city = st.text_input('Enter Provider City')
                    state = st.text_input('Enter Provider state i.e. CA, AZ')
                    zip = st.text_input('Enter Provider Zip Code')
                    providerLocation = f'{street_address} {city} {state} {zip}'
                    updateProvider_df.loc[providerId, "Provider Location"] = providerLocation
                elif selection == "Provider Email":
                    providerEmail = st.text_input("New Provider Email")
                    updateProvider_df.loc[providerId, "Provider Email"] = providerEmail


        

        with st.form('submitProviderUpdate', clear_on_submit = True):
            submitted = st.form_submit_button('Submit Provider Update')
            if submitted:
                updateProvider_df.to_csv(Path('./providers/providerList.csv'))
                '''tx_hash = contract.functions.updateProvider(
                    providerName,
                    accounts[0],
                    clinicName
                ).transact({'from' : st.session_state.updateProviderUser})
                # Display the information on the webpage
                receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
                st.write(receipt)'''
                st.write(updateProvider_df.loc[providerId])
                st.session_state.updateProviderName = ''
                st.experimental_rerun()

def page_viewProviders():
    st.header('View Providers')
    st.markdown('**If you would like to add or update providers, please click on the corresponding radio buttons on the left sidebar')
    try:
        providers_df = pd.read_csv(Path('./providers/providerList.csv'), index_col=[0]).astype(str)
        st.write(providers_df)
    except:
        st.write('No providers to display!  Please add a provider to the list if needed by clicking on the "Add Provider radio button on the left sidebar"')
                
                            

                    
          