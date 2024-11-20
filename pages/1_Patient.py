import streamlit as st 
from Home import setup

client = setup()

st.title("Chat with an AI Patient")

# Write chat history
for message in st.session_state.p_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat logic
if prompt := st.chat_input("Write a response here", disabled = st.session_state.response_counter >= 10):

    st.session_state["part_1_done"] = True

    st.session_state.p_chat_history.append({"role": "user", "content": prompt})

    if st.session_state.response_counter < 10:
    
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
        
        st.session_state.p_chat_history.append({"role": "assistant", "content": "Thanks for the help, doc."})
