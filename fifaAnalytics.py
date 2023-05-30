import pandas as pd
import streamlit as st
import plotly.express as px
import gspread


def read_google_sheet():
    gc = gspread.service_account(filename='token/fifaanalytics-388315-1fd8e7cff382.json')
    sh = gc.open("FIFA-tracker")
    rows = sh.sheet1.get_all_records()
    return rows

print(read_google_sheet())
