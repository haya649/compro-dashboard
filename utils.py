import streamlit as st
import requests
import time  # ★ timeモジュールをインポート

# この関数は、10分間（600秒）結果をキャッシュする
@st.cache_data(ttl=600)
def get_api_data(url):
    """APIからデータを取得する（キャッシュ機能付き）"""
    try:
        # ★ APIを呼び出す前に、必ず1秒待つ
        time.sleep(1) 
        
        response = requests.get(url)
        # 成功したらJSONデータを返す
        return response.json()
    except Exception as e:
        # 失敗したらエラーメッセージを返し、Noneを返す
        st.error(f"APIエラー: {url} の取得に失敗 - {e}")
        return None
