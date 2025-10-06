import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    st.error("GROQ_API_KEY not found. Please set it in your .env file.")
    st.stop()

def get_conversation_chain(model, memory):
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model
    )
    return ConversationChain(llm=groq_chat, memory=memory)

def main():
    st.title("Groq Chat App")

    st.sidebar.title('Select an LLM')
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama-3.1-8b-instant', 'moonshotai/kimi-k2-instruct-0905', 'groq/compound-mini']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

    if st.sidebar.button("Clear Chat History"):
        st.session_state.chat_history = []

    memory = ConversationBufferWindowMemory(k=conversational_memory_length)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Restore memory from chat history
    for message in st.session_state.chat_history:
        memory.save_context({'input': message['human']}, {'output': message['AI']})

    # Show the latest message first (if exists)
    user_question = st.text_area("Ask a question:")

    show_history = st.checkbox("Show previous chat history", value=False)

    if user_question and user_question.strip():
        conversation = get_conversation_chain(model, memory)
        response = conversation(user_question)
        message = {'human': user_question, 'AI': response['response']}
        st.session_state.chat_history.append(message)
        # Display only the latest message
        st.markdown("### Latest Message")
        st.markdown(f"**You:** {user_question}")
        st.markdown(f"**Chatbot:** {response['response']}")

    elif st.session_state.chat_history:
        # Display only the latest message if no new question
        latest_msg = st.session_state.chat_history[-1]
        st.markdown("### Latest Message")
        st.markdown(f"**You:** {latest_msg['human']}")
        st.markdown(f"**Chatbot:** {latest_msg['AI']}")

    # Show previous chat history if checkbox is checked
    if show_history and len(st.session_state.chat_history) > 1:
        st.markdown("### Previous Chat History")
        for msg in reversed(st.session_state.chat_history[:-1]):
            st.markdown(f"**You:** {msg['human']}")
            st.markdown(f"**Chatbot:** {msg['AI']}")

if __name__ == "__main__":
    main()