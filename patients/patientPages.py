import streamlit as st
from utils.contract import load_contract, get_provider
import pandas as pd
from pathlib import Path

contract = load_contract()
w3, node_provider = get_provider()
accounts = w3.eth.accounts

patient_filter = contract.events.logNewPatient.createFilter(fromBlock='latest')


#establish initial patients dataframe
patient_df_columns = ["Patient Name",
                "Patient Location",
                "Patient Neighborhood",
                "Preferred Language",
                "Needs Delivery",
                "Delivery Reason",
                "Phone Number",
                "Is Quarantined",
                "Provider",
                "Patient Consent",
                "Patient Organization",
                "Patient Age"]


if "patientName" not in st.session_state:
    st.session_state.patientName = ''
if "patientConsents" not in st.session_state:
    st.session_state.patientConsents = True

def page_addPatient():
   

    patient_df = pd.DataFrame(index = [0], columns = patient_df_columns).astype(str)


    st.header('Add a Patient')
    input_address = accounts[0]

    with st.form('newPatient', clear_on_submit=True):

        col1, col2 = st.columns(2)
        with col1:
            needsDelivery = st.radio('Does patient need delivery of goods?', options = ['Yes', 'No'])
            if needsDelivery == 'Yes':
                needsDelivery = True
            else:
                needsDelivery = False
            deliveryReason = st.selectbox('If patient needs delivery please select a reason', options = ['Quarantine', 'New Born Delivery', 'Surgery', 'Mobility Impairment', 'Other'])
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
            is_quarintined = st.radio('Is your patient quarantining because of Covid-19?', options = ['Yes', 'No'])
            patientFirstName = st.text_input('Patient First Name')
            patientLastName = st.text_input('Patient Last Name')
            patientName = f'{patientFirstName} {patientLastName}'
            preferredLanguage = st.text_input("Patient's preferred language?")
            patientPhoneNumber = st.text_input("Patient's Phone #", value='')
            patientNeighborhood = st.selectbox("Patient's Neighborhood", options = ['Bayview-Hunters Point', 'Bernal Heights', 'Excelsior', 'Ingelside', 'Mission','Mission Bay','Oceanview','Portola','Sunnydale','Tenderloin'])
            submitted = st.form_submit_button('Add Patient')


        if submitted:
            tx_hash = contract.functions.addPatient(
                patientName,
                patientConsents,
                input_address
            ).transact({'from' : input_address})
            # Display the information on the webpage
            receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
            st.write(receipt)
            newPatientId = contract.functions.getNewPatientId().call()
            st.markdown(f'Thank you.  Your patient, **{patientName}**, has been added to our list.  Their patient ID is **{newPatientId}**.  Please keep a record of this as it will be used for requests specific to this patient.')
            new_patient_df = pd.DataFrame(index = [newPatientId], columns = patient_df_columns).astype(str)

            new_patient_df.loc[newPatientId] = {
                "Patient Name" : patientName,
                "Patient Location" : patientLocation,
                "Patient Neighborhood" : patientNeighborhood,
                "Preferred Language" : preferredLanguage,
                "Needs Delivery" : needsDelivery,
                "Delivery Reason" : deliveryReason,
                "Phone Number" : patientPhoneNumber,
                "Is Quarantined" : is_quarintined,
                "Provider" : input_address,
                "Patient Consent" : patientConsents,
                "Patient Organization" : patientOrganization,
                "Patient Age" : patientAge
                }
            
            try:
                patient_df = pd.read_csv(Path('./patients/patientsList.csv'), index_col = [0]).astype(str)
                patient_df = pd.concat([patient_df, new_patient_df]).astype(str)
                
            except Exception:
                patient_df = new_patient_df.astype(str)

            patient_df.to_csv(Path('./patients/patientsList.csv'))

            if st.session_state.page == "Make Request":
                st.write("Back to requests now")
                st.experimental_rerun()
    
   
   
def page_updatePatient():

    updatePatient_df = pd.DataFrame()

    st.header('Update Patient Info')
    try:
        updatePatient_df = pd.read_csv(Path('./patients/patientsList.csv'), index_col = [0]).astype(str)
       
    except:
        st.markdown("### No patients to update")
        st.stop()
    
    
    with st.form('addPatientLookup'):
        input_address = accounts[0]
        patientNames = pd.Series(updatePatient_df["Patient Name"])
        patientNames = patientNames.values
        updatePatientName = st.selectbox('Select Patient to Update:', options = patientNames)
        st.session_state.patientName = updatePatientName
        addPatient = st.form_submit_button("Lookup Patient")
        if addPatient:
            patientId = updatePatient_df.loc[updatePatient_df['Patient Name'] == st.session_state.patientName].index
            patientId = patientId[0]
            st.session_state.patientId = patientId
            
            st.markdown('**Current Patient Info on File:**')
            patientInfo = pd.DataFrame(updatePatient_df.loc[st.session_state.patientId])
            st.write(patientInfo)
    
           
    st.markdown('**Please select the column[s] you would like to edit:**')

    updateSelect = (st.multiselect('', options = ["Patient Name","Patient Location","Patient Neighborhood","Preferred Language","Needs Delivery","Delivery Reason","Phone Number","Is Quarantined", "Patient Consent","Patient Organization","Patient Age"]))
    updateSelections = pd.Series(updateSelect)

    
    col1, col2 = st.columns(2)
    if updateSelections.empty != True:
        for selection in updateSelections:
            with col1:
                if selection == 'Needs Delivery':
                    needsDelivery = st.radio('Does patient need delivery of goods?', options = ['Yes', 'No'])
                    if needsDelivery == 'Yes':
                        updatePatient_df.loc[[st.session_state.patientId],'Needs Delivery'] = True
                    else:
                        updatePatient_df.loc[[st.session_state.patientId],'Needs Delivery'] = False
                elif selection == 'Delivery Reason':
                    deliveryReason = st.selectbox('Reason for delivery need',options = ['Quarantine', 'New Born Delivery', 'Surgery', 'Mobility Impairment', 'Other'])
                    updatePatient_df.loc[st.session_state.patientId, "Delivery Reason"] = deliveryReason
                elif selection == 'Patient Location':
                    patientLocation = st.markdown(f"**Enter new patient location:**")
                    street_address = st.text_input('Enter patient street address')
                    city = st.text_input('Enter Patient City')
                    state = st.text_input('Enter Patient state i.e. CA, AZ')
                    zip = st.text_input('Enter Patient Zip Code')
                    patientLocation = f'{street_address} {city} {state} {zip}'
                    updatePatient_df.loc[st.session_state.patientId, "Patient Location"] = patientLocation
                    
                elif selection == 'Patient Organization':
                    patientOrganization = st.text_input("Enter new organization name")
                    updatePatient_df.loc[st.session_state.patientId, "Patient Organization"] = patientOrganization
                    
                elif selection == 'Patient Age':    
                    patientAge = st.number_input("Patient's Age")
                    updatePatient_df.loc[st.session_state.patientId, "Patient Age"] = patientAge
                

            with col2:
                if selection == 'Patient Consent':            
                    patientsConsents = st.radio(f'New Consent Status', options = ['Yes', 'No'])
                    
                    if patientsConsents == 'Yes':
                        st.session_state.patientConsents = True
                    else:
                        st.session_state.patientConsents = False 
                    updatePatient_df.loc[st.session_state.patientId, "Patient Consent"] = st.session_state.patientConsents
                
                elif selection == 'Is Quarantined': 
                    is_quarintined = st.radio('Is patient quarantining for Covid-19?', options = ['Yes', 'No'])            
                    updatePatient_df.loc[st.session_state.patientId, "Is Quarantined"] = is_quarintined
                elif selection == 'Patient Name':
                    patientName = st.text_input('Enter new patient name')
                    updatePatient_df.loc[st.session_state.patientId, "Patient Name"] = patientName
                
                
                elif selection == 'Preferred Language':  
                    preferredLanguage = st.text_input("Patient's preferred language?")
                    updatePatient_df.loc[st.session_state.patientId, "Preferred Language"] = preferredLanguage
                    
                elif selection == 'Phone Number':      
                    patientPhoneNumber = st.text_input("Patient's Phone #")
                    updatePatient_df.loc[st.session_state.patientId, "Phone Number"] = patientPhoneNumber 

                elif selection == 'Patient Neighborhood':  
                    patientNeighborhood = st.selectbox("Patient's Neighborhood", options = ['Bayview-Hunters Point', 'Bernal Heights', 'Excelsior', 'Ingelside', 'Mission','Mission Bay','Oceanview','Portola','Sunnydale','Tenderloin'])
                    updatePatient_df.loc[st.session_state.patientId, "Patient Neighborhood"] = patientNeighborhood
        with st.form('updatePatient', clear_on_submit=True):
            submitted = st.form_submit_button('Update Patient')

            if submitted:
                updatePatient_df = updatePatient_df.astype(str)
                updatePatient_df.to_csv(Path('./patients/patientsList.csv'))
                tx_hash = contract.functions.updatePatient(
                    int(st.session_state.patientId),
                    st.session_state.patientName,
                    st.session_state.patientConsents
                ).transact({'from' : input_address})
                # Display the information on the webpage
                receipt = st.write(w3.eth.waitForTransactionReceipt(tx_hash))
                st.write(receipt)

                
                
                st.markdown(f"Thank you!  Your update of patient **{st.session_state.patientName}** with patient Id **{st.session_state.patientId}** has been accepted. Please confirm the new details below:")
                st.write(updatePatient_df.loc[st.session_state.patientId])            

def page_viewPatients():
    st.header('View patients')
    st.markdown("**Please note, by default you will only be able to view your own patients' info for privacy reasons.  If you need to get information about other patients, please contact the system administrator.**")
    try:
        patients_df = pd.read_csv(Path('./patients/patientsList.csv'), index_col=[0]).astype(str)
        st.write(patients_df)
    except:
        st.write("No patients to view")
def page_viewMyPatients():
    st.write('placeholder')