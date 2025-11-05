import streamlit as st
import pandas as pd
from utils import get_api_data  
import time
st.title("競プロ学習ダッシュボード")
st.header("メインページ：ユーザ概要")

if 'username' not in st.session_state:
    st.session_state.username = ""

username = st.sidebar.text_input("AtCoder IDを入力してください", st.session_state.username)
st.session_state.username = username 

if username:
    
    url_rank = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/ac_rank?user={username}"
    data_rank = get_api_data(url_rank)
    
    url_history = f"https://atcoder.jp/users/{username}/history/json"
    data_history = get_api_data(url_history)
    
    if data_rank and data_history:
        st.subheader(f"{username}さんのサマリー")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(label="AC数", value=f"{data_rank.get('count', 0)} 問")
        
        col2.metric(label="AC数ランク", value=f"{data_rank.get('rank', 'N/A')} 位")

        try:
            df_history = pd.DataFrame(data_history)
            rated_history = df_history[df_history['NewRating'] > 0]

            if not rated_history.empty:
                current_rate = rated_history['NewRating'].iloc[-1]
                highest_rate = rated_history['NewRating'].max()
                
                col3.metric(label="現在レート", value=f"{current_rate}")
                col4.metric(label="最高レート", value=f"{highest_rate}")
            else:
                col3.metric(label="現在レート", value="N/A")
                col4.metric(label="最高レート", value="N/A")
        except Exception:
            col3.metric(label="現在レート", value="Error")
            col4.metric(label="最高レート", value="Error")
            
    else:
        st.error("データの取得に失敗しました。IDが正しいか確認してください。")
        
    st.subheader("最新のAC履歴 (5件)")

    half_year_ago = int(time.time()) - (365 * 24 * 60 * 60 // 2)

    url_submissions = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={username}&from_second={half_year_ago}"
    data_submissions = get_api_data(url_submissions)
    
    if data_submissions:
        df_submissions = pd.DataFrame(data_submissions)

        st.write(f"取得した提出件数: {len(df_submissions)} 件")

        first_sub_time = pd.to_datetime(df_submissions['epoch_second'].min(), unit='s')
        last_sub_time = pd.to_datetime(df_submissions['epoch_second'].max(), unit='s')

        st.write(f"取得したデータの期間: {first_sub_time} から {last_sub_time} まで")
        


        ac_df = df_submissions[df_submissions['result'] == 'AC'].copy()
        
        if not ac_df.empty:
            ac_df['time'] = pd.to_datetime(ac_df['epoch_second'], unit='s') + pd.Timedelta(hours=9)
            ac_df_display = ac_df.drop_duplicates(subset='problem_id')
            st.dataframe(
                ac_df_display[['time', 'problem_id', 'contest_id', 'point']].sort_values(by='time', ascending=False).head(5)
            )
        else:
            st.write("AC履歴がありません")

else:
    st.warning("サイドバーからAtCoder IDを入力してください")
