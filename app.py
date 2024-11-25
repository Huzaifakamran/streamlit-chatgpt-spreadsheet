import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from openai import OpenAI
import json 

def chatGPT(user_query, data):
    # Format data as key-value pairs
    formatted_data = "\n".join([f"{key}: {value}" for key, value in data.items()])
    print(formatted_data)
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"]) 
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. You need to reply to the user query based on the following information:\n{formatted_data}"},
            {"role": "user", "content": user_query}
        ]
    )
    return completion.choices[0].message.content

# Google Sheets fetch data function
def fetch_data():
    creds_dict = {
  "type": st.secrets["type"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email":st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url":st.secrets["client_x509_cert_url"],
  "universe_domain": st.secrets["universe_domain"]
}

    creds_json = json.dumps(creds_dict)
    # Google Sheets setup
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]
    # creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    # client = gspread.authorize(creds)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)


    # Open the spreadsheet and select the first worksheet
    sheet = client.open("Listing Inventory Data").sheet1
    return sheet.get_all_values()  # Fetch all records

# Initialize session state
if "stored_row" not in st.session_state:
    st.session_state["stored_row"] = None

# Streamlit app
st.title("Google Sheets ID Checker")

# Input ID
input_id = st.text_input("Enter a keyword to search:")

if input_id:
    data = fetch_data()
    
    # Searching the first column for the input ID
    found = False
    for row in data[1:]:  # Skip the header row
        keys = row[0].split(",")  # Split comma-separated keys
        if input_id in keys:
            st.session_state["stored_row"] = dict(zip(data[0], row))  # Store as a key-value dictionary
            st.write(f"Match found! Initial response:\n\n {row[1]}")
            found = True
            break

    if not found:
        st.warning("ID not found in any row.")

# If a row has been stored, enable further interactions
if st.session_state["stored_row"]:
    st.divider()
    st.write("You can now ask questions related to the stored details.")
    user_query = st.text_input("Ask a question about the details:")

    if user_query:
        response = chatGPT(user_query, st.session_state["stored_row"])
        print("RESPONSE",response)
        st.write(response)
