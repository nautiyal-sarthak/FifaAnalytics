import pandas as pd
import streamlit as st
import plotly.express as px
import gspread


def read_google_sheet():
    gc = gspread.service_account(filename='token/fifaanalytics-388315-1fd8e7cff382.json')
    sh = gc.open("FIFA-tracker")
    rows = sh.sheet1.get_all_records()
    return rows

def createDatafrme(formatedList):
    df = pd.DataFrame(formatedList)

    # Extract time component into a separate column
    df['Time'] = pd.to_datetime(df['Timestamp']).dt.hour

    # Convert 'DateTime' column to datetime type
    df['Date'] = pd.to_datetime(df['Timestamp']).dt.date



    return df

if __name__ == "__main__":
    # read the details from the google sheet
    formatedList = read_google_sheet()
    #create a dataframe
    df = createDatafrme(formatedList)
    print(df)

    #Prepare the dashboard
    st.title("FifaAnalytics")

    # 1.