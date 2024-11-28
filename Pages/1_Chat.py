import json
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
import math
import numpy as np
import google.generativeai as genai
import os



genai.configure(api_key="AIzaSyDqXlh83m8LivN-Nt2FeVVNUdTpvMqSwfk")    
model = genai.GenerativeModel('gemini-1.5-flash')

def genAnswer(prompt):
    response = model.generate_content(prompt)
    output_text = response.text
    return output_text

#This is to create the storage for the messages:

st.markdown(
    """
    <style>
    .sticky-title {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: white;
        padding: 10px;
        z-index: 1000;
        border-bottom: 2px solid #f0f0f0;
    }
    </style>
    <div class="sticky-title">
        <h1>Cloud-Based ChatBot</h1>
    </div>
    """,
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

#Display the chat history:
# st.write(st.session_state.messages)
for messages in st.session_state.messages:
    with st.chat_message(messages.get("role")):
        st.write(messages.get("content"))

prompt = st.chat_input("Ask anything")
if prompt:
    st.session_state.messages.append({"role" : "user", "content" : prompt})
    with st.chat_message("user"):
        st.write(prompt)
        answer = genAnswer(prompt)

    st.session_state.messages.append({"role" : "assistant", "content" : answer})
    with st.chat_message("assistant"):
        st.write(answer)


