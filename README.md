# GeoChat - Talk with a Digital Twin In Natural Language

gkvoelkl@nelson-games.de

<img src="img/start.jpg" width="320" align="left"><br><br><br><br><br><br><br><br><br><br><br><br>

Normally, the data that makes up a **digital twin** is displayed in **3D**.
This looks good but is not easy to use and understand.

Programs like **ChatGPT** and other **LLMs** have shown how to **easily bring huge amounts of information to people**.

With technologies such as

* LlamaIndex,
* ChromaDB,
* OpenAI API,
* Ollama or
* Streamlit,

it is relatively easy to create a **natural language interface** for a digital twin and its geoinformation.


# Part 1: How many Buildings?

My **first digital twin** consists of the **buildings of a large city** that I got **from OpenStreetMap**. These are stored in a **relational database (postgresql)**.

<img src="img/db1.png" width="320" align="left"><br><br><br><br><br><br><br><br><br><br><br><br>

An **LLM** turns the **user's question** into a suitable **query to the database**.
And a suitable answer from the data received.

Some examples:

🤖 Chat: Ask me a question about the Database!

👤 User: How many buildings?

🤖 Chat:There are a total of 931,866 buildings in the database.

👤 User: I stand in Baker Street. Where is the next bank?

🤖 Chatbot: The nearest bank to Baker Street is TSB located in London with the postcode W1U 7DL. It is right on Baker Street itself.

<img src="img/chat1.png" width="320" align="left"><br><br><br><br><br><br><br><br><br><br><br><br>


```python
%%writefile geochat.py
import streamlit as st

from sqlalchemy import create_engine, MetaData
from geoalchemy2 import Geometry

from llama_index import SQLDatabase, ServiceContext
from llama_index.llms import OpenAI
from llama_index.indices.struct_store import NLSQLTableQueryEngine
        
import pandas
from pprint import pprint

# -- connect to openai
import openai

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

        sql_database = SQLDatabase(
            engine, 
            include_tables=include_tables,
            custom_table_info = custom_table_info
        )

        llm = OpenAI(
            temperature=0.1,
            model="gpt-3.5-turbo"
        )
    
    service_context = ServiceContext.from_defaults(
        llm=llm
    )

    return sql_database, service_context, engine


sql_database, service_context, engine = load_data()

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
        service_context = service_context,
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

```


```python
!streamlit run geochat.py
```

    [0m
    [34m[1m  You can now view your Streamlit app in your browser.[0m
    [0m
    [34m  Local URL: [0m[1mhttp://localhost:8501[0m
    [34m  Network URL: [0m[1mhttp://192.168.178.78:8501[0m
    [0m
    [34m[1m  For better performance, install the Watchdog module:[0m
    
      $ xcode-select --install
      $ pip install watchdog
                [0m



```python

```
