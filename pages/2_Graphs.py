import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import get_api_data  # utils.py から関数をインポート

st.title("学習グラフ")

# --- メインページからIDを引き継ぐ ---
if 'username' not in st.session_state or not st.session_state.username:
    st.warning("メインページでAtCoder IDを入力してください")
    st.stop() # IDがなければ、ここで処理を停止

username = st.session_state.username 
st.sidebar.text(f"Atcoder ID : {username}")
# --- ★ タブを作成 ★ ---
tab_ac, tab_rate = st.tabs(["📊 提出分析", "📈 レート変動"])

# -----------------------------------------------
# グラフ1：「提出分析」タブ
# -----------------------------------------------
with tab_ac:
    st.header(f"{username}さんの提出状況")
    
    # --- 提出履歴データの取得 ---
    url_submissions = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={username}&from_second=0"
    data_submissions = get_api_data(url_submissions)

    if data_submissions:
        df_submissions = pd.DataFrame(data_submissions)
        
        # --- (1) 提出結果のパイチャート ---
        st.subheader("提出結果の割合")
        result_counts = df_submissions["result"].value_counts()
        fig_pie = px.pie(
            result_counts,
            values=result_counts.values,
            names=result_counts.index,
            title="提出結果"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- (2) 日別AC数のグラフ ---
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


# -----------------------------------------------
# グラフ2：「レート変動」タブ
# -----------------------------------------------
with tab_rate:
    st.header(f"{username}さんのレート変動")
    try:
        url_history = f"https://atcoder.jp/users/{username}/history/json"
        data_history = get_api_data(url_history) # 共通関数を使う

        if data_history:
            df_history = pd.DataFrame(data_history)
            rated_history = df_history[df_history['NewRating'] > 0].copy()

            if not rated_history.empty:
                
                # --- ▼▼▼ ここから変更 ▼▼▼ ---
                st.subheader("レートサマリー")
                
                # 3つの列を作成
                col1, col2, col3 = st.columns(3)

                # 1. 参加回数を計算
                col1.metric(label="Rated参加回数", value=f"{len(rated_history)} 回")
                
                # 2. 最高レートを計算
                highest_rate = rated_history['NewRating'].max()
                col2.metric(label="最高レート", value=f"{highest_rate}")
                
                # 3. 現レートを計算 (リストの最後の値)
                current_rate = rated_history['NewRating'].iloc[-1]
                col3.metric(label="現在レート", value=f"{current_rate}")
                # --- ▲▲▲ ここまで変更 ▲▲▲ ---

                # レート変動グラフを表示
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
