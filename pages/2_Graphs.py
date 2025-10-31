import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

st.title("学習グラフ")

# --- メインページからIDを引き継ぐ ---
if 'username' not in st.session_state or not st.session_state.username:
    st.warning("メインページでAtCoder IDを入力してください")
    st.stop() # IDがなければ、ここで処理を停止

username = st.session_state.username 

# -----------------------------------------------
# グラフ1：日別AC数のグラフ
# -----------------------------------------------
st.header(f"{username}さんの提出状況")

try:
    url_submissions = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={username}&from_second=0"
    response_submissions = requests.get(url_submissions)
    data_submissions = response_submissions.json()

    if data_submissions:
        df_submissions = pd.DataFrame(data_submissions)

        st.subheader("提出結果の割合")
        result_counts = df_submissions["result"].value_counts()
        
        fig = px.pie(
            result_counts,
            values=result_counts.values,
            names=result_counts.index,
            title="提出結果"
        )
        
        st.plotly_chart(fig, use_container_width=True)


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

except Exception as e:
    st.error(f"提出履歴の取得に失敗しました: {e}")


# -----------------------------------------------
# グラフ2：AtCoderレート変動グラフ
# -----------------------------------------------
st.header(f"{username}さんのレート変動")

# 1. テキストエリアで入力を受け付ける
# ★★★ 新しく発見したURLに修正 ★★★
try:
    # ★★★ 新しく発見したURLに修正 ★★★
    url_history = f"https://atcoder.jp/users/{username}/history/json"
    
    response_history = requests.get(url_history)
    data_history = response_history.json()

    if data_history:
        df_history = pd.DataFrame(data_history)
        
        # 'NewRating' が0より大きいものだけ（Ratedコンテストのみ）に絞り込む
        rated_history = df_history[df_history['NewRating'] > 0].copy()

        if not rated_history.empty:
            # 日時を日本時間に変換
            rated_history['time'] = pd.to_datetime(rated_history['EndTime'])
            # グラフ描画のために、インデックスを日時に設定
            rated_history = rated_history.set_index('time')
            
            # レート（NewRating）の変動グラフを表示
            st.line_chart(rated_history['NewRating'])
        else:
            st.write("Ratedコンテストの参加履歴がありません")
    else:
        st.write("コンテスト参加履歴がありません")
        
except Exception as e:
    st.error(f"コンテスト履歴の取得に失敗しました: {e}")
