import streamlit as st

from sqlalchemy import create_engine, MetaData
from geoalchemy2 import Geometry

from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import NLSQLTableQueryEngine
       
import pandas

USE_OPENAI = True

# -- connect to openai
import openai

if USE_OPENAI:
    openai.api_key = st.secrets.openai_key

# -- include tables
include_tables = ["osm_buildings"]

# -- page config
title = "GeoChat - Talk with your Data 💬 📚"
st.set_page_config(
    page_title=title,
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.header(title)

# -- init message history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", 
         "content": "Ask me a question about the Database!"}
    ]

# -- prepare data
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Initalizing Data – hang tight! This should take 1-2 minutes."):
        url = 'postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/postgres'
        engine = create_engine(url)
    
        custom_table_info = {
            "osm_buildings": "stores all the buildings of a great city"
        }

        if USE_OPENAI:
            Settings.llm = OpenAI(
                temperature=0.1,
                model="gpt-3.5-turbo"
            )
        else:
            Settings.llm = Ollama(
                model="llama2", 
                request_timeout=120.0
            )
            
        sql_database = SQLDatabase(
            engine, 
            include_tables=include_tables,
            custom_table_info = custom_table_info
        )

    return sql_database, engine


sql_database, engine = load_data()

# -- Sidebar
def sidebar_infos(engine):
    st.sidebar.image("./img/logo.png",
                     width = 50,
                     use_column_width=None)
    
    st.sidebar.markdown("## Database")

    metadata = MetaData()
    metadata.reflect(bind=engine)

    table_names = include_tables # metadata.tables.keys()
    selected_table = st.sidebar.selectbox("Select a Table", table_names)
        
    if selected_table:
        table = metadata.tables[selected_table]
        columns_info = [{'Column': column.name, 'Type': str(column.type)} for column in table.columns]
        df = pandas.DataFrame(columns_info, index=None)
        st.sidebar.dataframe(df)
                
    # Sidebar Intro
    st.sidebar.markdown('## Created By')
    st.sidebar.markdown("gkvoelkl@nelson-games.de")
    
    st.sidebar.markdown('## Disclaimer')
    st.sidebar.markdown("This application is only for demonstration purposes.")

st.sidebar.header("GeoChat")
info_on = st.sidebar.toggle('Activate info')
sidebar_infos(engine)

# -- create engine
if "query_engine" not in st.session_state:
    st.session_state["query_engine"] = NLSQLTableQueryEngine(
        sql_database = sql_database,
        #streaming=True
    )    

# -- ask user
if prompt := st.chat_input("Your question"):
    st.session_state.messages.append( # save prompt
        {"role": "user", 
         "content": prompt}
    )

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# -- get answer
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state["query_engine"].query("User Question:"+prompt+". ")
            if info_on:
                st.info(f"sql {response.metadata['sql_query']}",icon="ℹ️")
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
