import streamlit as st
from azure.cosmos import CosmosClient, exceptions
import uuid
import json
from streamlit_extras.switch_page_button import switch_page
import requests
import math
import numpy as np
import google.generativeai as genai
import os

# Replace with your Cosmos DB credentials
COSMOS_URI = os.getenv("COSMOS_URI")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "myDatabase"
CONTAINER_NAME = "Users"

# Initialize Cosmos Client
client = CosmosClient(COSMOS_URI, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

def login(username, password):
    try:
        # Query for user
        query = f"SELECT * FROM c WHERE c.userID = '{username}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if items and items[0]["password"] == password:
            return {"status": "success", "message": "Login successful."}
        else:
            return {"status": "error", "message": "Invalid username or password."}
    except exceptions.CosmosHttpResponseError as e:
        return {"status": "error", "message": str(e)}

def signup(username, password):
    try:
        # Check if the user already exists
        query = f"SELECT * FROM c WHERE c.userID = '{username}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        if items:
            return {"status": "error", "message": "User already exists."}

        # Add new user with a unique id
        user_id = str(uuid.uuid4())  # Generate a unique id
        container.create_item({"id": user_id, "userID": username, "password": password})
        return {"status": "success", "message": "User created successfully."}

    except exceptions.CosmosHttpResponseError as e:
        return {"status": "error", "message": str(e)}

# Check if the user is already logged in via session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# Display sidebar navigation if logged in
if st.session_state.logged_in:
    # Show the sidebar for navigation after login
    page = st.sidebar.radio("Choose a page", ["Chat", "Login"])

    # Switch between pages based on selection
    if page == "Chat":
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
    elif page == "Login":

        # Display the login form if the user is not logged in
        st.title("Login/Sign Up")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # Check if the user clicked the "Login" button
        if st.button("Login"):
            response = login(username, password)
            if response["status"] == "success":
                st.success(response["message"])
                st.session_state.logged_in = True  # Set the session to logged-in
                st.rerun()  # Re-run to show the sidebar and navigate
            else:
                st.error(response["message"])

        # Display a sign-up form
        st.write("Don't have an account? Sign up below.")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        # Check if the user clicked the "Sign Up" button
        if st.button("Sign Up"):
            if new_password == confirm_password:
                response = signup(new_username, new_password)
                if response["status"] == "success":
                    st.success(response["message"])
                else:
                    st.error(response["message"])
            else:
                st.error("Passwords do not match. Please try again.")
else:
    # Display the login form if the user is not logged in
    st.title("Login/Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Check if the user clicked the "Login" button
    if st.button("Login"):
        response = login(username, password)
        if response["status"] == "success":
            st.success(response["message"])
            st.session_state.logged_in = True  # Set the session to logged-in
            st.rerun()  # Re-run to show the sidebar and navigate
        else:
            st.error(response["message"])

    # Display a sign-up form
    st.write("Don't have an account? Sign up below.")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    # Check if the user clicked the "Sign Up" button
    if st.button("Sign Up"):
        if new_password == confirm_password:
            response = signup(new_username, new_password)
            if response["status"] == "success":
                st.success(response["message"])
            else:
                st.error(response["message"])
        else:
            st.error("Passwords do not match. Please try again.")
