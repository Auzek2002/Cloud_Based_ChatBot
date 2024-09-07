import json
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests

def login(username, password):
    # print(f'{username}, {password}')
    headers = {
    'Content-Type': 'application/json'}
    url='http://localhost:5000/user/login'
    body={'userID':username, 'password':password}
    body_json=json.dumps(body)
    # print(body_json)
    response = requests.post(url=url,headers=headers, data=body_json)
    # print('Status Code:', response.status_code)
    # print('Response Body:', response.json())
    return response
    # pass

def signup(username, password):
    headers = {
    'Content-Type': 'application/json'}
    url='http://localhost:5000/user/signup'
    body={'userID':username, 'password':password}
    body_json=json.dumps(body)
    # print(body_json)
    response = requests.post(url=url,headers=headers, data=body_json)
    # print('Status Code:', response.status_code)
    # print('Response Body:', response.json())
    return response
    pass

st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
# Define the valid username and password
# valid_username = "user"
# valid_password = "password"

# Page title
st.title("Login/Sign Up Page")

# Display the login form
username = st.text_input("Username")
password = st.text_input("Password", type="password")

# Check if the user clicked the "Login" button
if st.button("Login"):
    # response = login(username,password)

    # if(response.status_code==200):#successfull login
    # # if username == valid_username and password == valid_password:
    #     response=response.json()
    #     st.session_state.token = response['authorization']
    #     st.success("Login successful!")
    #     st.markdown("""
    # <style>
    #     section[data-testid="stSidebar"][aria-expanded="true"]{
    #         display: block;
    #     }
    # </style>
    # """, unsafe_allow_html=True)
    if username == 'Azaan' and password == '123':
         st.success("Login successful!")
         st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: block;
        }
    </style>
    """, unsafe_allow_html=True)


    else:
        st.error("Invalid username or password. Please try again.")

# Display a sign-up form
st.write("Don't have an account? Sign up below.")
new_username = st.text_input("New Username")
new_password = st.text_input("New Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")

# Check if the user clicked the "Sign Up" button
if st.button("Sign Up"):
    if new_password == confirm_password:
        response = signup(new_username,new_password)
        if(response.status_code==200):
            st.success("Account created successfully! Please login.")
        else:    
            st.error("User Already Exists. Please login or chose another username")
    else:
        st.error("Passwords do not match. Please try again.")


