import streamlit as st
import requests
import time 

@st.cache_data(ttl=600)
def get_api_data(url):

    try:
       
        time.sleep(1) 
        response = requests.get(url)
        
        return response.json()
    except Exception as e:
       
        st.error(f"APIエラー: {url} の取得に失敗 - {e}")
        return None
