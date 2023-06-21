import pandas as pd
import streamlit as st
import plotly.express as px
import gspread
import datetime
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go


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
    #df = df.drop('Timestamp',axis=1)
    return df

def getWinner(score,p1,p2):
    scorelst = score.split("-")
    winner = "Tied"

    if scorelst[0] > scorelst[1]:
        winner = p1
    elif scorelst[0] < scorelst[1]:
        winner = p2

    return winner


def isCleanSheet(score):
    flag = 0
    if '0-0' not in score :
        scorelst = score.split("-")

        if '0' in scorelst:
            flag = 1

    return flag



def createDatafrme(formatedList):
    df = pd.DataFrame(formatedList)
    return df

def formatDataframe(df):
    #adding date cols
    df = getDateTimeFeilds(df)

    #get the winner
    df['winner'] = df.apply(lambda row: getWinner(row['fulltime score'], row['Home player'], row['Away player']), axis=1)
    df['is_cleansheet'] = df.apply(lambda row: isCleanSheet(row['fulltime score']),
                            axis=1)

    return df

def getWins(df):
    wins = df.groupby(['winner', 'Date']).count()['Home team'].reset_index()\
        .rename(columns={"Home team":"Wins"})
    return wins

def getPieAndTrend(df):
    pie_fig = px.pie(df, values='Wins', names='winner')

    trend_fig = px.bar(df, x="Date", y="Wins", color='winner',barmode="group")
    #trend_fig = go.Scatter(x=df['Date'], y=df['Wins'], line_shape='spline')

    return pie_fig , trend_fig

def getGoalsPieAndTrend(df):
    pie_fig = px.pie(df, values='GoalsScored', names='Player')

    trend_fig = px.bar(df, x="Date", y="GoalsScored", color='Player',barmode="group")

    return pie_fig , trend_fig

def getResult(score,perspective):
    src_lst = score.split('-')
    result = "Tie"

    if perspective == 'home':
        if src_lst[0] > src_lst[1]:
            result = "Won"
        elif src_lst[1] > src_lst[0]:
            result = "Lost"

    elif perspective == 'away':
        if src_lst[0] > src_lst[1]:
            result = "Lost"
        elif src_lst[1] > src_lst[0]:
            result = "Won"

    return result

def getGoals(df):
    homeDF = df[['Timestamp','Date','Home team','Home player','fulltime score']]
    homeDF['GoalsScored'] = [x[0] for x in homeDF['fulltime score'].str.split("-")]
    homeDF['GoalsConceded'] = [x[1] for x in homeDF['fulltime score'].str.split("-")]
    homeDF['Result'] = homeDF['fulltime score'].apply(getResult, args=('home',))
    homeDF['stadium'] = 'Home'
    homeDF = homeDF.rename({'Home team': 'Team', 'Home player': 'Player'}, axis=1)


    awayDF = df[['Timestamp','Date','Away team', 'Away player', 'fulltime score']]
    awayDF['GoalsScored'] = [x[1] for x in awayDF['fulltime score'].str.split("-")]
    awayDF['GoalsConceded'] = [x[0] for x in awayDF['fulltime score'].str.split("-")]
    awayDF['Result'] = awayDF['fulltime score'].apply(getResult, args=('away',))
    awayDF['stadium'] = 'Away'
    awayDF = awayDF.rename({'Away team': 'Team', 'Away player': 'Player'}, axis=1)

    returndf = pd.concat([homeDF, awayDF])

    returndf = returndf.astype({'GoalsScored': 'int','GoalsConceded':'int'})

    return returndf

def make_grid(cols,rows):
    grid = [0]*cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    page_bg_img = '''
        <style>
        body {
        background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
        background-size: cover;
        }
        </style>
        '''

    st.markdown(page_bg_img, unsafe_allow_html=True)

    # read the details from the google sheet
    formatedList = read_google_sheet()
    #create a dataframe
    df = createDatafrme(formatedList)
    formatedDf = formatDataframe(df)

    #Prepare the dashboard
    st.title("Fifa Analytics")


    fig1 , fig2 = getPieAndTrend(getWins(formatedDf))
    mygrid = make_grid(3,2)



    mygrid[0][0].header("Wins Analysis")

    mygrid[1][0].plotly_chart(fig1)

    with mygrid[1][1] :
        selected_points = plotly_events(fig2)

    if (selected_points):
        a = selected_points[0]
        st.text("Match Results for " + a['x'])
        dt_lst = str(a['x']).split('-')
        st.dataframe(
            formatedDf[formatedDf['Date'] == datetime.date(int(dt_lst[0]), int(dt_lst[1]), int(dt_lst[2]))].drop('Time',
                                                                                                                 axis=1).drop(
                'Date', axis=1))

    allGoalsDf = getGoals(formatedDf)
    grpGoals = allGoalsDf.groupby(['Player', 'Date'])['GoalsScored'].sum().reset_index()

    mygrid3 = make_grid(2, 2)
    mygrid3[0][0].header("Clean sheets")

    cleansheet = formatedDf.groupby(['winner']).sum('is_cleansheet').reset_index() \
        .rename(columns={"is_cleansheet": "cleansheet"})

    cleansheet = cleansheet[cleansheet['winner'] != 'Tied']

    cleansheet_fig = px.pie(cleansheet, values='cleansheet', names='winner')

    mygrid3[1][0].plotly_chart(cleansheet_fig)
    filterdf = formatedDf[formatedDf['is_cleansheet'] == 1]
    mygrid3[1][1].dataframe(filterdf[['Home team','Away team','Home player','Away player','fulltime score','winner','Date']])


    fig3, fig4 = getGoalsPieAndTrend(grpGoals)
    mygrid2 = make_grid(2, 2)

    mygrid2[0][0].header("Goals Analysis")
    mygrid2[1][0].plotly_chart(fig3)
    mygrid2[1][1].plotly_chart(fig4)


    st.title("Player analysis")
    option = st.selectbox('Select a player',set(allGoalsDf['Player']))

    if option != "" :

        selPlayerdf = allGoalsDf[allGoalsDf["Player"]==option]

        # selPlayerdf['is_cleansheet'] = selPlayerdf.apply(lambda row: isCleanSheet(row['fulltime score']),
        #                                axis=1)
        # st.dataframe(selPlayerdf)

        statsDF = selPlayerdf.groupby(['stadium','Team',])\
            .agg(
                {"Date":"count",
                "GoalsScored":"sum",
                "GoalsConceded":"sum",
                #"is_cleansheet":"sum",
                "Result":lambda x: list(x)}
                 )\
            .reset_index()\
            .rename(columns={"Date":"total_games",
                            "GoalsScored":"total_goals_scored",
                            "GoalsConceded":"Total Goals Conceded"})

        mygrid3 = make_grid(2, 2)

        mygrid3[0][0].header("Team selection")
        mygrid3[1][0].plotly_chart(px.pie(statsDF[statsDF['stadium']=='Home'], values='total_games', names='Team',title='Home Teams'))
        mygrid3[1][1].plotly_chart(px.pie(statsDF[statsDF['stadium'] == 'Away'], values='total_games', names='Team',title='Away Teams'))

        bestmatch = formatedDf[formatedDf['winner']==option]
        bestmatch['goal_diff'] = [abs(int(x[0])- int(x[1])) for x in bestmatch['fulltime score'].str.split("-")]\


        bestmatch =  bestmatch.sort_values(by=['goal_diff'],
                                                 ascending=[False])
        st.header("Best Performace")
        st.dataframe(bestmatch.iloc[0:3])

        statsDF["total_wins"] = statsDF['Result'].apply(lambda x: x.count("Won"))
        statsDF["total_tie"] = statsDF['Result'].apply(lambda x: x.count("Tie"))
        statsDF["total_lost"] = statsDF['Result'].apply(lambda x: x.count("Lost"))

        statsDF["win%"] = (statsDF['total_wins']/statsDF['total_games']) * 100
        statsDF["goal_diff"] = statsDF['total_goals_scored'] - statsDF['Total Goals Conceded']


        statsDF['goals/game'] = statsDF['goal_diff'] / statsDF['total_games']
        statsDF['weighted_win%'] = statsDF['win%'] * statsDF['total_games']
        statsDF['factor'] = statsDF["win%"] + (statsDF['weighted_win%'])

        statsDF['factor'] = (statsDF['total_games'] +  ((statsDF["total_wins"]) * 1.5) +
                             ((statsDF['total_lost']) * -2.5) + ((statsDF['total_tie']) * 1))


        statsDF["Recent Form"] = statsDF['Result'].apply(lambda x: x[:5])


        statsDF = statsDF[['stadium','factor','Team','total_games','total_lost','total_tie','total_wins','goal_diff','win%','goals/game','Recent Form']]



        homeDf = statsDF[statsDF['stadium']=='Home']
        homeDf = homeDf[['Team', 'total_games', 'total_wins','total_lost','total_tie', 'goal_diff', 'win%', 'goals/game', 'Recent Form','factor']]

        awayDf = statsDF[statsDF['stadium'] == 'Away']
        awayDf = awayDf[
            ['Team', 'total_games', 'total_wins','total_lost','total_tie', 'goal_diff', 'win%', 'goals/game', 'Recent Form','factor']]

        if not homeDf.empty :
            #best Home team
            st.subheader("Best Home Team")

            sorted_teams = homeDf.sort_values(by=['factor','goals/game'],
                                                 ascending=[False,False])


            st.dataframe(sorted_teams.iloc[0:3])


            #wort Home team
            st.subheader("Worst Home Team")
            sorted_teams = homeDf.sort_values(by=['factor','goals/game'],
                                              ascending=[True,True])

            st.dataframe(sorted_teams.iloc[0:3])

        if not awayDf.empty:
            #best Away team
            st.subheader("Best Away Team")
            sorted_teams = awayDf.sort_values(by=['factor','goals/game'],
                                              ascending=[False,False])

            st.dataframe(sorted_teams.iloc[0:3])


            #worst Home team
            st.subheader("Worst Away Team")
            sorted_teams = awayDf.sort_values(by=['factor','goals/game'],
                                              ascending=[True,True])

            st.dataframe(sorted_teams.iloc[0:3])