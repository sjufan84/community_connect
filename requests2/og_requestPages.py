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
