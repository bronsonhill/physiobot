import streamlit as st
from Home import setup
from utils.mongodb import log_transcript

if not bool(st.session_state.get("user_identifier", "").strip()):
    st.error("Please enter your identifier on the Home page before starting the conversation.")
    st.stop()

MAXIMUM_RESPONSES = 1000

client = setup()

st.title("Chat with your Patient")

# Write chat history
for message in st.session_state.p_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat logic
if prompt := st.chat_input(
    "Write a response here",
    disabled=st.session_state.p_conversation_finished or st.session_state.response_counter >= MAXIMUM_RESPONSES
):

    st.session_state["part_1_done"] = True

    st.session_state.p_chat_history.append({"role": "user", "content": prompt})

    if st.session_state.response_counter < MAXIMUM_RESPONSES:
    
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            messages_with_system_prompt = [{"role": "system", "content": st.session_state["patient_prompt"]}] + [
                {"role": m["role"], "content": m["content"]}
            for m in st.session_state.p_chat_history
            ]

            stream = client.chat.completions.create(
                model = st.session_state["model"],
                messages = messages_with_system_prompt,
                stream = True,
            )
            response = st.write_stream(stream)

        st.session_state.response_counter += 1
        st.session_state.p_chat_history.append({"role": "assistant", "content": response})

    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            st.markdown("Thanks for the help, doc.")
        
        final_message = {"role": "assistant", "content": "Thanks for the help, doc."}
        st.session_state.p_chat_history.append(final_message)
        st.session_state.p_conversation_finished = True

# Add finish conversation button below chat input
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.p_conversation_finished and st.session_state.p_chat_history:
        if st.button("Finish Conversation", key="finish_patient", use_container_width=True):
            st.session_state.p_conversation_finished = True
            session_id = log_transcript(
                st.session_state["mongodb_uri"],
                "patient",
                st.session_state.p_chat_history
            )
            st.session_state.session_id = session_id
            st.rerun()