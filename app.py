import streamlit as st
import requests
import pandas as pd
from datetime import datetime # 日時を扱うために追加

st.title("競プロ学習ダッシュボード")
st.header("メインページ：AC数")

if "username" not in st.session_state:
    st.session_state.username = ""

username = st.sidebar.text_input("AtCoder IDを入力してください", st.session_state.username)
st.session_state.username = username

if st.sidebar.button("学習状況を表示"):
    if username:
        # 提出履歴を取得するAPIエンドポイント
        url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={username}&from_second=0"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            # --- ここから改良 ---
            if data:
                # 1. データをDataFrameに変換
                df = pd.DataFrame(data)
                
                # 2. ACしたものだけを抜き出す
                ac_df = df[df['result'] == 'AC'].copy()
                
                # 3. AC数を表示
                st.write(f"## {username}さん のAC数")
                st.write(f"**{len(ac_df.problem_id.unique())} 問** (ユニーク問題数)") # 重複を除いた問題数

                # 4. ACした問題リストを表示
                st.write("--- ACした問題リスト (最新50件) ---")
                
                # 見やすいように列を絞り込み、重複を除外
                ac_df_display = ac_df.drop_duplicates(subset='problem_id')
                
                # 日時を日本時間に変換
                ac_df_display['time'] = pd.to_datetime(ac_df_display['epoch_second'], unit='s') + pd.Timedelta(hours=9)
                
                # 新しい順にソートして表示
                st.dataframe(
                    ac_df_display[['time', 'problem_id', 'contest_id', 'point']].sort_values(by='time', ascending=False).head(50)
                )
                
            else:
                st.write(f"## {username}さん のAC数")
                st.write("**0 問**")
            # --- ここまで ---

        except Exception as e:
            st.error(f"データの取得に失敗しました: {e}")
    else:
        st.warning("IDを入力してください")
