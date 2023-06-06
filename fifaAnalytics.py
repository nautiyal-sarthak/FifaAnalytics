import pandas as pd
import streamlit as st
import plotly.express as px
import gspread


def read_google_sheet():
    gc = gspread.service_account(filename='token/fifaanalytics-388315-1fd8e7cff382.json')
    sh = gc.open("FIFA-tracker")
    rows = sh.sheet1.get_all_records()
    return rows

def getDateTimeFeilds(df):
    # formating date feilds
    # Extract time component into a separate column
    df['Time'] = pd.to_datetime(df['Timestamp']).dt.hour

    # Convert 'DateTime' column to datetime type
    df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
    df = df.drop('Timestamp',axis=1)
    return df

def getWinner(score,p1,p2):
    scorelst = score.split("-")
    winner = "Tied"

    if scorelst[0] > scorelst[1]:
        winner = p1
    elif scorelst[0] < scorelst[1]:
        winner = p2

    return winner

def createDatafrme(formatedList):
    df = pd.DataFrame(formatedList)
    return df

def formatDataframe(df):
    #adding date cols
    df = getDateTimeFeilds(df)

    #get the winner
    df['winner'] = df.apply(lambda row: getWinner(row['fulltime score'], row['Home player'], row['Away player']), axis=1)

    return df

def getWins(df):
    wins = df.groupby(['winner', 'Date']).count()['Home team'].reset_index()\
        .rename(columns={"Home team":"Wins"})
    return wins

if __name__ == "__main__":
    # read the details from the google sheet
    formatedList = read_google_sheet()
    #create a dataframe
    df = createDatafrme(formatedList)
    formatedDf = formatDataframe(df)
    print(formatedDf)

    #Prepare the dashboard
    st.title("FifaAnalytics")

    st.dataframe(formatedDf)
    st.dataframe(getWins(formatedDf))

    # 1.

    fig = px.pie(getWins(formatedDf), values='Wins', names='winner', title='Win %')
    st.plotly_chart(fig)

    fig = px.bar(getWins(formatedDf), x="Date", y="Wins", color='winner')
    st.plotly_chart(fig)