import streamlit as st
from openai import OpenAI

st.title("Homepage")
st.markdown(
    "Welcome! For this activity, you will interact with a chatbot roleplaying as a patient. " \
    "The aim is to practice the subjective assessment framework and the communication skills required to establish therapeutic rapport and support patients." \
)
st.markdown(
    "1. Apply the subjective assessment framework to the AI patient. Only when you are finished the conversation click the `finish` button. You will not be able to undo this submission.\n" \
    "2. Converse with the AI Supervisor to receive feedback and assessment on your conversation with the AI patient. Again, only when you are finished the conversation click the `finish` button. You will not be able to undo this submission.\n" \
)

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

    # Set up OpenAI API client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    return client


