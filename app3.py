import os
import json
from tkinter import N
from turtle import onclick
from numpy import true_divide
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import singleton_functions
import yfinance as yf
import requests
from PIL import Image
import plotly.graph_objects as go
import datetime as dt
import pytz

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
    with open(Path('./contracts/compiled/CC3_abi.json')) as f:
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
# @ TODO create way for wallets to connect to the wallet using javascript and MetaMask?
accounts = w3.eth.accounts
nonprofit = accounts[0]
supplier_address = accounts[4]
supplier_key = os.getenv("SUPPLIER_PRIVATE_KEY")
nonprofit_key = os.getenv('NONPROFIT_PRIVATE_KEY')
donor = accounts[0]

patient_filter = contract.events.logNewPatient.createFilter(fromBlock='latest')
request_filter = contract.events.logNewRequest.createFilter(fromBlock='latest')


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

#Establishing our dataframes to store our ledger
block_chain_df = pd.DataFrame()
new_df = pd.DataFrame()




def main():
    if "page" not in st.session_state:
        # Initialize session state.
        st.session_state.update({
            # Default page.
            "page": "home",

            # Default patient id
            "patientId" : 0
        })

    st.sidebar.subheader("How Can We Help?")
    page = st.sidebar.radio('', options=tuple(PAGES.keys()))
    st.sidebar.markdown("""---""")
    
    PAGES[page]()




def page_home(): #st.header("""This is a decentralized application that facilitates an ecosystem of donors, non-profits, and end users in the distribution of aid""")
    st.sidebar.title("Community Connect App")
    #st.image('Resources/CommunityConnect_image.png', use_column_width='auto')

    


def page_addPatient():

    st.header('Add a Patient')
    st.markdown('**If you are not already a registered provider, please register before submitting requests**')
    newProvider = st.button('Register as a new provider')
    if newProvider:
        page_addProvider()
    
    input_address = st.selectbox('Your wallet address', options =[accounts[0]])

    with st.form('newPatient', clear_on_submit=True):

        col1, col2 = st.columns(2)
        with col1:
            needsDelivery = st.radio('Does patient need delivery of goods?', options = ['Yes', 'No'])
            if needsDelivery == 'Yes':
                needsDelivery = True
            else:
                needsDelivery = False
            deliveryReason = st.selectbox('If patient needs delivery please select a reason', options = ['quarintine', 'New Born Delivery', 'Surgery', 'Mobility Impairment', 'Other'])
            if deliveryReason:
                deliveryReason = deliveryReason
            street_address = st.text_input('Enter patient street address')
            city = st.text_input('Enter Patient City')
            state = st.text_input('Enter Patient state i.e. CA, AZ')
            zip = st.text_input('Enter Patient Zip Code')
            patientLocation = f'{street_address} {city} {state} {zip}'
            patientOrganization = st.text_input('If the patient is already a member of an organization, please write it here')
            patientAge = st.number_input("Patient's Age", value=0)

            

        with col2:
            patientConsents = st.radio('Does your patient consent to sharing their personal information with the Patient Pantry and its partners in order to keep track and receive funding?', options = ['Yes', 'No'])
            if patientConsents == 'Yes':
                patientConsents = True
            else:
                patientConsents = False
            is_quarintined = st.radio('Is your patient quarintining becasue of Covid-19?', options = ['Yes', 'No'])
            if is_quarintined == 'Yes':
                is_quarintined = True
            else:
                is_quarintined = False
            patientFirstName = st.text_input('Patient First Name')
            patientLastName = st.text_input('Patient Last Name')
            patientName = f'{patientFirstName} {patientLastName}'
            preferredLanguage = st.text_input("Patient's preferred language?")
            patientPhoneNumber = st.text_input("Patient's Phone #")
            patientNeighborhood = st.selectbox("Patient's Neighborhood", options = ['Bayview-Hunters Point', 'Bernal Heights', 'Excelsior', 'Ingelside', 'Mission','Mission Bay','Oceanview','Portola','Sunnydale','Tenderloin'])
            submitted = st.form_submit_button('Add Patient')

        if submitted:
            tx_hash = contract.functions.addPatient(
                patientLocation,
                patientName,
                patientConsents,
                deliveryReason,
                is_quarintined,
                needsDelivery,
                preferredLanguage,
                patientPhoneNumber,
                patientNeighborhood,
                patientOrganization,
                patientAge
            ).transact({'from' : input_address})
            # Display the information on the webpage
            receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
            st.write(receipt)
            event = patient_filter.get_new_entries()
            eventDict = dict(event[0]['args'])
            patientName = eventDict['_patientName']
            patientId = eventDict['patientId']
            st.markdown(f"Thank you!  Your addition of **{patientName}** has been accepted.  Their **CommunityConnect Id Number is {patientId}.**  Please keep this for your records and give it to them as they will need to reference it in the future.  You can also use it to submit requests on their behalf and to update or reference their information in the system.")
            #your location below:**")

            
            #block_chain_df = singleton_functions.update_block_chain_df(receipt, w3)
            #new_df = updateIPFS_df(contract, block_chain_df, nonprofit)
            
            #st.write(f'{requestLocation}')
            #st.write(block_chain_df)

def page_updatePatient():
    st.header('Update Patient Info')

def page_addProvider():
    st.header('New Provider')

def page_newRequest():
    st.header('New Request')

    st.subheader('Please fill out request details below')
    st.markdown('**If the patient you are requesting for has not been registered in the system, please click below to register them before submitting a goods request.**')
    addPatient = st.button('Add New Patient')
    if addPatient:
        page_addPatient()
    patientId = st.number_input('Enter Patient Id for Request', value=0)
    submitPatient = st.button('Lookup Patient Id')
    if submitPatient:
        patientInfo = contract.functions._patients(patientId).call()
    
        col1, col2 = st.columns(2)

        with col1:
            patientName = f'{patientInfo[6]}'
            st.markdown(f'**Patient Name:**  {patientName}')
            patientLocation = f'{patientInfo[1]}'
            st.markdown(f'**Patient Location:**  {patientLocation}')
            patientNeighborhood = f'{patientInfo[9]}'
            st.markdown(f'**Patient Neighborhood:**  {patientNeighborhood}')
            preferredLanguage = f'{patientInfo[5]}'
            st.markdown(f"**Patient's preferred language is:**  {preferredLanguage}")
        with col2:
            needsDelivery = {patientInfo[0]} 
            st.markdown(f'**Patient Needs Delivery:**  {needsDelivery}')
            patientPhoneNumber = f'{patientInfo[8]}'
            st.markdown(f'**Patient Phone #:**  {patientPhoneNumber}')
            is_quarintined = f'{patientInfo[4]}'
            st.markdown(f'**Patient is quarintined?**  {is_quarintined}')
        
        
        st.markdown('**If any of the above information is incorrect and needs to be updated, please click below to update patient information, otherwise continue the request below:**')
        updateInfo = st.button("Update Patient Information")
        if updateInfo:
            st.session_state.patientId = patientId
            page_updatePatient()

        with st.form("submitRequest", clear_on_submit=True):
            currentTime = dt.datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')

            providerWallet = st.selectbox('Provider, please select your address here', options=[accounts[0]])

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
                st.write('submitted')
                tx_hash = contract.functions.addPatient(
                patientName,
                patientLocation,
                needsDelivery,
                preferredLanguage,
                patientPhoneNumber,
                patientNeighborhood,
                patientId,
                providerWallet,
                foodItemType,
                prepConsiderations,
                babyItems,
                clothesSizes,
                personalCareType,
                numAdults,
                numChildren,
                sizeDiapers,
                sleepSurface,
                otherSpecialItems,
                otherPatientNotes,
                currentTime,
                ageGenderChildren
            ).transact({'from' : providerWallet})
                # Display the information on the webpage
                receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
                st.write(receipt)
                event = request_filter.get_new_entries()
                eventDict = dict(event[0]['args'])
                patientName = eventDict['_patientName']
                patientId = eventDict['patientId']
                st.markdown(f"Thank you!  Your addition of **{patientName}** has been accepted.  Their **CommunityConnect Id Number is {patientId}.**  Please keep this for your records and give it to them as they will need to reference it in the future.  You can also use it to submit requests on their behalf and to update or reference their information in the system.")
                #your location below:**")

            
            #block_chain_df = singleton_functions.update_block_chain_df(receipt, w3)
            #new_df = updateIPFS_df(contract, block_chain_df, nonprofit)
            
            #st.write(f'{requestLocation}')
            #st.write(block_chain_df)


        '''col1, col2 = st.columns(2)
        with col1:
            newName = st.text_input('What is the name of the product?')
            newProductType = st.selectbox('Select type of assistance requested', options = ['Food', 'Supplies'])
        
        # Input quantity of items requested if food or supplies, else ride quantity defaults to 1
        with col2:
            owner_address = st.selectbox('Select your wallet address to submit request form', options = accounts[5:10])
            newProductCount = st.number_input('Enter product quantity requested', value=1)
            
        submitted = st.form_submit_button("Register Request")
        if submitted:

            # Displays map of requesters location for confirmation
            requestLocation = f'{street_address} {city} {state} {zip}'
            endpoint = "mapbox.places" 
            try:
                response = requests.get(url=f'https://api.mapbox.com/geocoding/v5/{endpoint}/{requestLocation}.json?access_token={mapbox_access_token}').json()
                latitude = response['features'][0]['center'][1]
                longitude = response['features'][0]['center'][0]

                fig = go.Figure(go.Scattermapbox(lat=[latitude], lon=[longitude], 
                    mode='markers', marker=go.scattermapbox.Marker(size=18, symbol='car')))

                fig.update_layout(hovermode='closest', title = f'{requestLocation}', mapbox=dict(
                    accesstoken=mapbox_access_token, bearing=0, center=go.layout.mapbox.Center(
                    lat=latitude, lon=longitude), pitch=0, zoom=15))
            
            except Exception:
                fig = ''
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
            
            block_chain_df = singleton_functions.update_block_chain_df(receipt, w3)
            new_df = updateIPFS_df(contract, block_chain_df, nonprofit)

            st.markdown("**Thank you!  Your request is pending supplier confirmation!  Please confirm\
            your location below:**")
            #st.write(f'{requestLocation}')
            if fig != '':
                st.plotly_chart(fig, title=f'{requestLocation}')
            else:
                st.markdown(f'{requestLocation}')

            st.markdown('**Transaction Hash:**')
            st.write(block_chain_df)'''


def page_viewRequests():
    st.header('View Requests')

PAGES = {
    "Home" : page_home,
    "Add Patient": page_addPatient,
    "Update Patient": page_updatePatient,
    "Make Request": page_newRequest,
    "View Open Requests": page_viewRequests,
    "New Provider": page_addProvider
}

if __name__ == "__main__":
    main()








