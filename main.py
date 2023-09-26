import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
import openai
from llama_index.readers.database import DatabaseReader
import random
import pandas as pd


footer_html = """
    <div class="footer">
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f0f2f6;
            padding: 10px 20px;
            text-align: center;
        }
        .footer a {
            color: #4a4a4a;
            text-decoration: none;
        }
        .footer a:hover {
            color: #3d3d3d;
            text-decoration: underline;
        }
    </style>
        Made for Streamlit LLM Hackathon. Powered by LlamaIndex 🦙
    </div>
"""

page_bg_img = f"""
<style>
  /* Existing CSS for background image */
  [data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://i.postimg.cc/4xgNnkfX/Untitled-design.png");
    background-size: cover;
    background-position: center center;
    background-repeat: no-repeat;
    background-attachment: local;
  }}
  [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
  }}

  /* New CSS to make specific divs transparent */
  .stChatFloatingInputContainer, .css-90vs21, .e1d2x3se2, .block-container, .css-1y4p8pa, .ea3mdgi4 {{
    background-color: transparent !important;
  }}
</style>
"""


@st.cache_resource(show_spinner=False)
def load_index(_docs):
    with st.spinner(text="Loading and indexing the docs – hang tight!"):
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4", temperature=0))
        index = VectorStoreIndex.from_documents(_docs, service_context=service_context)
        return index


@st.cache_data(show_spinner=False)
def load_docs(query):
    with st.spinner(text="Loading and indexing the docs – hang tight!"):

        snowflake_user = st.secrets["connections"]["snowflake"]['user']
        snowflake_password = st.secrets["connections"]["snowflake"]['password']
        snowflake_account = st.secrets["connections"]["snowflake"]['account']
        snowflake_database = st.secrets["connections"]["snowflake"]['database']
        snowflake_schema = st.secrets["connections"]["snowflake"]['schema']

        snowflake_url = f"snowflake://{snowflake_user}:{snowflake_password}@{snowflake_account}/{snowflake_database}/{snowflake_schema}"

        reader = DatabaseReader(uri=snowflake_url)
        docs = reader.load_data(query=query)

        # add column names to metadata
        for doc in docs:
            doc.metadata['columns'] = "region, quarter, quota, profit, commission, revenue"
            
        return docs


def get_user_identity(df):
    # Randomly select a row from the DataFrame
    random_index = random.choice(df.index)
    random_row = df.loc[random_index]

    name = random_row['employee_name']
    photo_url = random_row['photo']

    # Drop the 'Employee_ID' column
    df.drop('employee_id', axis=1, inplace=True)
    df.drop('photo', axis=1, inplace=True)

    # Concatenate column names and their values
    concatenated_str = ', '.join([str(random_row[col]) for col in df.columns])

    # Update session_state
    st.session_state.user_identity = concatenated_str
    st.session_state.photo_url = photo_url
    return name.split(' ')[0]


@st.cache_data(show_spinner=False)
def load_data(query):
    # Initialize connection.
    conn = st.experimental_connection('snowflake', type='sql')

    # Perform query.
    df = conn.query(query)
    return df


st.set_page_config(page_title="SalesWizz", page_icon="💸", layout="centered",
                   initial_sidebar_state="auto", menu_items=None)

st.markdown(page_bg_img, unsafe_allow_html=True)

# load employees table as df
query_emp = f"""
SELECT *
FROM EMPLOYEES
"""

# Load employees table
employees_df = load_data(query=query_emp)

# load employees table as df
query_sales = f"""
SELECT *
FROM SALESDATA
"""

# Set OpenAI API key
openai.api_key = st.secrets["openai_credentials"]["openai_key"]

# load sales table and index
sales_docs = load_docs(query=query_sales)
index = load_index(_docs=sales_docs)


st.title("SalesWizz: One Query Away from Your Sales 💸")

with st.expander('What this app is about?'):
    """
    This app is a basic implementation of a user-identity-aware chatbot.
    It is trained on internal sales data and follows the company's policy for handling IAM (Identity and Access Management).

    The model is trained on the fictional sales data including region, quarter, quota, profit, commission and revenue.

    The model is trained on the following policy:
    1. The sales data can only be shared with Account Executives or Directors.
    2. Account Executives can only be provided with data from their region. For example, an Account Executive from North America cannot get EMEA data and vice versa.
    3. No data must be shared with contractors, regardless of the role and region.
    4. The Directors can access data from all the regions (global).

    The model is instructed about the current user's identity and decides whether to share the data or not based on the policy. As a nice bonus, the app displays the current user's photo from the employee table in the chat window.

    High level architecture:
    """
    st.image('https://i.postimg.cc/VvhPYqLz/saleswizz-diagram.png', use_column_width=True)

    st.write('The chatbot is following the logic below:')

    st.image('https://i.postimg.cc/K86N8M3h/model-logic.png', use_column_width=True)


# Initialize session state if it's not already initialized
if 'user_identity' not in st.session_state:
    st.session_state.user_identity = None

if st.session_state.user_identity is None:
    name = get_user_identity(df=employees_df)

info = f"""
You are randomly assigned a user identity. Your current identify is: **{st.session_state.user_identity}**. Click the button below to shuffle the identity.
\n
You can ask about quota, profit, commission or revenue. The data is available for the following regions: North America, EMEA, Asia, LATAM. And for the following quarters: Q1, Q2, Q3, Q4.
"""

st.info(info, icon="📃")

policy = f"""
You're helpful internal chatbot assistant, your task is answering questions about company sales data. You don't have knowledge of any other topics.
Your responses should differ depending on who you are chatting with. You must follow the company policy outlined below:

1. You can only share sales data with these roles: Account Executive, Director.
2. Account Executives can only be provided with data from their region. For example, an Account Executive from North America cannot get EMEA data and vice versa.
3. You must not share any data with contractors, regardless of the role and region.
4. The Directors can access all data from all the regions (global data).

Your reasoning should be the following:
1. Determine the role of the user. If the user is Director, proceed to step 4. If the user is Account Executive, proceed to step 2. Otherwise, decline to share any data.
2. Determine the region of the user. Is the user asking about their own region? If yes, proceed to step 3. If not, decline to share any data.
3. Determine employment type. Is the user a contractor? If yes, decline to share any data. If not, proceed to step 4.
4. Share the data.

If you cannot share data with a user, refer them to their manager. If a user is asking about "my quota/profit/commission/revenue", they mean their own region.
Follow these rules at all times and do not break them under any circumstances.
Do not hallucinate or make up the answers.

You are currently chatting with {st.session_state.user_identity}
"""


chat_engine = index.as_chat_engine(chat_mode="context", verbose=True, system_prompt=policy)

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": f"Hi {name}! How can I help you today?"}
    ]

if prompt := st.chat_input("Your question"):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})


for message in st.session_state.messages:  # Display the prior chat messages
    # if role is user
    if message["role"] == "user":
        with st.chat_message(message["role"], avatar=st.session_state.photo_url):
            st.write(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message(message["role"]):
            st.write(message["content"])


# create buttons for sample questions and to shuffle the user identity
col1, col2 = st.columns(2)

sample_questions = ["What's the Q3 revenue in my region?", "What's the Q2 quota in EMEA?", "What's the Q4 quota in Asia?", "What's the Q1 revenue in LATAM?",
                    "What's the Q3 revenue in North America?", "What's Q2 commission in LATAM?", "What is my Q1 quota?", "Is EMEA Q3 revenue higher than Q2?",
                    "What's the Q1 profit in my region?", "What's the Q2 commission in my region?"]

with col1:
    sample_q = st.button('Ask a sample question ❔')
if sample_q:
    # randomly select a sample question
    prompt = random.choice(sample_questions)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # display the message
    with st.chat_message("user", avatar=st.session_state.photo_url):
        st.write(prompt)


with col2:
    shuffle = st.button('Shuffle the user identity 🔄')
    if shuffle:
        # clear session state
        st.session_state.user_identity = None
        name = get_user_identity(df=employees_df)

        # update chat history
        st.session_state.messages = [
            {"role": "assistant", "content": f"Hi {name}! How can I help you today?"}
        ]
        st.experimental_rerun()

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message)  # Add response to message history


st.markdown(footer_html, unsafe_allow_html=True)
