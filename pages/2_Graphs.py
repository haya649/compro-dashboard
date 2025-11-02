import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import get_api_data

st.title("学習グラフ")


if 'username' not in st.session_state or not st.session_state.username:
    st.warning("メインページでAtCoder IDを入力してください")
    st.stop() 

username = st.session_state.username 
st.sidebar.text(f"Atcoder ID : {username}")

tab_ac, tab_rate = st.tabs(["📊 提出分析", "📈 レート変動"])


with tab_ac:
    st.header(f"{username}さんの提出状況")
    

    url_submissions = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={username}&from_second=0"
    data_submissions = get_api_data(url_submissions)

    if data_submissions:
        df_submissions = pd.DataFrame(data_submissions)

        st.subheader("提出結果の割合")
        result_counts = df_submissions["result"].value_counts()
        fig_pie = px.pie(
            result_counts,
            values=result_counts.values,
            names=result_counts.index,
            title="提出結果"
        )
        st.plotly_chart(fig_pie, use_container_width=True)


        st.subheader("日別AC数")
        ac_df = df_submissions[df_submissions['result'] == 'AC'].copy()
        
        if not ac_df.empty:
            ac_df['time'] = pd.to_datetime(ac_df['epoch_second'], unit='s') + pd.Timedelta(hours=9)
            daily_ac = ac_df.set_index('time').resample('D')['problem_id'].nunique()
            st.line_chart(daily_ac)
        else:
            st.write("AC履歴がありません")
            
    else:
        st.write("提出履歴がありません")


with tab_rate:
    st.header(f"{username}さんのレート変動")
    try:
        url_history = f"https://atcoder.jp/users/{username}/history/json"
        data_history = get_api_data(url_history)

        if data_history:
            df_history = pd.DataFrame(data_history)
            rated_history = df_history[df_history['NewRating'] > 0].copy()

            if not rated_history.empty:
                

                st.subheader("レートサマリー")
                

                col1, col2, col3 = st.columns(3)


                col1.metric(label="Rated参加回数", value=f"{len(rated_history)} 回")
                

                highest_rate = rated_history['NewRating'].max()
                col2.metric(label="最高レート", value=f"{highest_rate}")
                

                current_rate = rated_history['NewRating'].iloc[-1]
                col3.metric(label="現在レート", value=f"{current_rate}")

                st.subheader("レート変動グラフ")
                rated_history['time'] = pd.to_datetime(rated_history['EndTime'])
                rated_history = rated_history.set_index('time')
                st.line_chart(rated_history['NewRating'])
            else:
                st.write("Ratedコンテストの参加履歴がありません")
        else:
            st.write("コンテスト参加履歴がありません")
            
    except Exception as e:
        st.error(f"コンテスト履歴の取得に失敗しました: {e}")
