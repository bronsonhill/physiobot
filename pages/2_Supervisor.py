import streamlit as st
from Home import setup

st.title("Chat with an AI Supervisor")

client = setup()

if not st.session_state["part_1_done"]:
    st.write("Please complete Activity 1 (chat with the AI patient) first.")
    exit()

# Add chat history to supervisor prompt
p_messages = st.session_state["p_chat_history"]
formatted_messages = "\n".join([f"{message['role'].capitalize()}: {message['content']}" for message in p_messages])

systemprompt = f"{st.session_state['supervisor_prompt']} \n\n {formatted_messages}"

# Write chat history
for message in st.session_state.s_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat logic
if prompt := st.chat_input("Write a response here", disabled = st.session_state.response_counter_2 >= 1000):

    st.session_state.s_chat_history.append({"role": "user", "content": prompt})

    if st.session_state.response_counter_2 < 1000:
    
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            messages_with_system_prompt = [{"role": "system", "content": systemprompt}] + [
                {"role": m["role"], "content": m["content"]}
            for m in st.session_state.s_chat_history
            ]

            stream = client.chat.completions.create(
                model = st.session_state["model"],
                messages = messages_with_system_prompt,
                stream = True,
            )
            response = st.write_stream(stream)

        st.session_state.response_counter_2 += 1
        st.session_state.s_chat_history.append({"role": "assistant", "content": response})

    else:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            st.markdown("Good job today.")
        
        st.session_state.s_chat_history.append({"role": "assistant", "content": "Good job today."})





