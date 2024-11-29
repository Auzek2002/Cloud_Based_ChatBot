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
import cvzone
from cvzone.HandTrackingModule  import HandDetector
import cv2
import mediapipe as mp
from PIL import Image

# Replace with your Cosmos DB credentials
COSMOS_URI = "https://icc-project.documents.azure.com:443/"
COSMOS_KEY = "Wqb4X2RwLti3B5IDYrwATzGTws2phkbT5vYCWtiYgtKBR2JgAeXWPTaQkMXBaaaHkOplmLXzE1whACDbNQp2ig=="
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
    page = st.sidebar.radio("Choose a page", ["Chat", "Draw"])

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
    elif page == "Draw":

        st.title("""Welcome to The Draw a Problem Section!""")
        st.write("""#### Draw with your Index Finger!""")
        st.write("""#### Show first 3 fingers to clear the canvas!""")
        st.write("""#### Show Thumb and Pinky finger to get the answer!""")

        col_1 , col_2 = st.columns([2,1])

        with col_1:
            st.checkbox('Run',True)
            FRAMES = st.image([])

        with col_2:
            st.title(" Answer")
            output_area = st.subheader("")

        #----------------------------------------------------------------------------------MODEL CODE ------------------------------------------------------------------------------------------------------

        genai.configure(api_key="AIzaSyDqXlh83m8LivN-Nt2FeVVNUdTpvMqSwfk")     
        model = genai.GenerativeModel('gemini-1.5-flash')

        #-----------------------------------------------------------------------------------CV CODE ---------------------------------------------------------------------------------------------------------

        #Initialize the webcam to capture video:
        cap = cv2.VideoCapture(0)
        cap.set(3,1280)
        cap.set(4,720)

        detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
        def getDetectedHands(img):
            hands, img = detector.findHands(img, draw=True, flipType=True)

            if hands:
                hand1 = hands[0] 
                lmList = hand1["lmList"]
                fingers1 = detector.fingersUp(hand1)
                return fingers1,lmList
            else:
                return None
            

        def draw(img,info,prev_pos,canvas,color=(255,0,255)):
            fingers , lmlist = info
            current_pos = None
            #To draw use Index Finger
            if fingers == [0,1,0,0,0]:
                current_pos= lmlist[8][0:2]
                if prev_pos is None: prev_pos = current_pos
                cv2.line(canvas,current_pos,prev_pos,(255,0,255),10)
            
            #To clear screen/canvas show first 3 Fingers
            elif fingers == [0,1,1,1,0]:
                canvas = np.zeros_like(img)
            
            return current_pos, canvas


        def genAnswer(info,canvas):
            fingers , lmlist = info
            #To send to AI Show NO Fingers
            if fingers == [1,0,0,0,1]:
                questionImg = Image.fromarray(canvas)
                response = model.generate_content(["Solve this Problem:",questionImg])
                output_text = response.text
                return output_text



        prev_pos = None
        canvas = None
        combinedImage = None
        output_text = ""


        while True:
            success, img = cap.read()
            img = cv2.flip(img,1)
            info = getDetectedHands(img)
            if canvas is None:
                canvas = np.zeros_like(img)
                combinedImage = img.copy()
            if info:
                fingers, lmlist = info
                prev_pos,canvas = draw(img,info,prev_pos,canvas)
                output_text = genAnswer(info,canvas)
                if output_text:
                    output_area.text(output_text)


            combinedImage = cv2.addWeighted(img,0.7,canvas,0.3,0)

            FRAMES.image(combinedImage,channels="BGR")

            #Display the image in a window:
            # cv2.imshow("Image", img)
            # cv2.imshow("Canvas", canvas)
            # cv2.imshow("Combined Image",combinedImage)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
else:
    # Display the login form if the user is not logged in
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
