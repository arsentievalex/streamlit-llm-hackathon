import streamlit as st
import random


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



@st.cache_data(show_spinner=False)
def load_data():
    # Initialize connection.
    conn = st.experimental_connection('snowpark')

    # Perform query.
    employees_df = conn.query('SELECT * from EMPLOYEES;')
    sales_df = conn.query('SELECT * from SALESDATA;')
    return employees_df, sales_df


def get_user_identity(df):
    # Randomly select a row from the DataFrame
    random_index = random.choice(df.index)
    random_row = df.loc[random_index]

    name = random_row['EMPLOYEE_NAME']
    photo_url = random_row['PHOTO']

    # Drop the 'Employee_ID' column
    df.drop('EMPLOYEE_ID', axis=1, inplace=True)
    df.drop('PHOTO', axis=1, inplace=True)

    # Concatenate column names and their values
    concatenated_str = ', '.join([str(random_row[col]) for col in df.columns])

    # Update session_state
    st.session_state.user_identity = concatenated_str
    st.session_state.photo_url = photo_url

    return name.split(' ')[0]


st.set_page_config(page_title="SalesWizz", page_icon="💸", layout="centered",
                   initial_sidebar_state="auto", menu_items=None)

st.markdown(page_bg_img, unsafe_allow_html=True)



st.title("SalesWizz: One Query Away from Your Sales 💸")

# Load data
employees_df, sales_df = load_data()

st.dataframe(employees_df)

