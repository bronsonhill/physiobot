import streamlit as st
from openai import OpenAI
from utils.mongodb import check_identifier

def is_identifier_valid():
    identifier = st.session_state.get("user_identifier", "").strip()
    if not identifier:
        return False
    return check_identifier(st.session_state["mongodb_uri"], identifier)

def setup():

    if "patient_prompt" not in st.session_state: 
        with open("./prompts/pprompt.txt", "r") as file:
            patientprompt = file.read()

        st.session_state["patient_prompt"] = patientprompt

    if "supervisor_prompt" not in st.session_state:
        with open("./prompts/supervisorprompt.txt", "r") as file:
            supervisorprompt = file.read()

        st.session_state["supervisor_prompt"] = supervisorprompt

    if "model" not in st.session_state:
        st.session_state["model"] = "gpt-4o-mini"

    if "p_chat_history" not in st.session_state:
        st.session_state["p_chat_history"] = []

    if "s_chat_history" not in st.session_state:
        st.session_state["s_chat_history"] = []

    if "response_counter" not in st.session_state:
        st.session_state["response_counter"] = 0

    if "response_counter_2" not in st.session_state:
        st.session_state["response_counter_2"] = 0
    
    if "part_1_done" not in st.session_state:
        st.session_state["part_1_done"] = False

    if "mongodb_uri" not in st.session_state:
        st.session_state["mongodb_uri"] = st.secrets["MONGODB_CONNECTION_STRING"]

    if "p_conversation_finished" not in st.session_state:
        st.session_state["p_conversation_finished"] = False
    
    if "s_conversation_finished" not in st.session_state:
        st.session_state["s_conversation_finished"] = False

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None

    if "user_identifier" not in st.session_state:
        st.session_state["user_identifier"] = ""

    # Set up OpenAI API client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    return client

def init_page():
    st.title("Homepage")
    st.markdown(
        "Welcome! For this activity, you will interact with a chatbot roleplaying as a patient. " \
        "The aim is to practice the subjective assessment framework and the communication skills required to establish therapeutic rapport and support patients." \
    )
    st.markdown(
        "## Instructions\n"
        "1. Enter your unique identifier below. This will be used to associate your conversation records with you.\n"
        "2. In the Patient Conversation tab, converse with your AI patient and apply the subjective assessment framework. Only when you are finished the conversation click the `finish` button. You will not be able to undo this submission.\n"
        "3. Converse with the AI Supervisor to receive feedback and assessment on your conversation with the AI patient. Again, only when you are finished the conversation click the `finish` button. You will not be able to undo this submission.\n"
        "\nNote: Please ensure you have a stable internet connection to prevent any issues from occurring."
    )

    # Add identifier input after welcome message
    identifier = st.text_input(
        "Please enter your unique identifier:",
        key="identifier_input",
        value=st.session_state.get("user_identifier", ""),
        help="This identifier will be stored with your conversation records"
    )

    if identifier:
        if check_identifier(st.session_state["mongodb_uri"], identifier):
            st.session_state["user_identifier"] = identifier
            st.success("✅ Identifier validated successfully. You can now proceed to the conversation pages.")
        else:
            st.error("❌ Invalid identifier. Please enter a valid identifier.")
            st.session_state["user_identifier"] = ""
    else:
        st.warning("⚠️ Please enter your identifier before starting any conversations.")

if __name__ == "__main__":
    init_page()


