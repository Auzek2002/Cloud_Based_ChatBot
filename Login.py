import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import uuid
from azure.cosmos import CosmosClient, exceptions

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

# Page title
st.title("Login/Sign Up Page")

# If user is logged in, show the content for logged-in users
if st.session_state.logged_in:
    # Show Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a page", ["Chat", "Draw"])

    if page == "Chat":
        switch_page("chat")
    elif page == "Draw":
        switch_page("draw")
else:
    # Display the login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Check if the user clicked the "Login" button
    if st.button("Login"):
        response = login(username, password)
        if response["status"] == "success":
            st.success(response["message"])
            st.session_state.logged_in = True  # Set the session to logged-in
            st.experimental_rerun()  # Re-run to show the sidebar and navigate
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
