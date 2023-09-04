# streamlit_app.py

import streamlit as st
import gspread
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

client=gspread.authorize(credentials)
sheet_url = st.secrets["gsheets"]["private_gsheets_url"] #this information should be included in streamlit secret
sheet = client.open_by_url(sheet_url).sheet1
dataframe = pd.DataFrame(sheet.get_all_records())
st.dataframe(dataframe)
#rows = sheet.get_values()
#for row in rows:
#    st.write(row)

