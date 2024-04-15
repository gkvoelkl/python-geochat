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

from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import NLSQLTableQueryEngine
       
import pandas
from pprint import pprint

USE_OPENAI = True

if USE_OPENAI:
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

```

    Overwriting geochat.py



```python
!streamlit run geochat.py
```

# Part 2: There is no Bakerstreet 🔍 in London! Challenges 🧩

When you try to talk to your **digital twin**, you **don't** always get the **answers you expect**.

🤖 Chat: Ask me a question about the Database!

👤 User: How many buildings are in Bakerstreet?

🤖 Chat: There are no buildings listed in the database for Bakerstreet.

After many questions, it turned out that there are three basic challenges.

### 🧩 Challenge 1️⃣: Values in Columns that are Difficult to Understand 

The LLM cannot find "Bakerstreet" because it is not written the way it is written in the database ("Baker Street") - **different spellings**.

The value range of an attribute is an important information for the LLM. Example: In a column the value “1” stands for "true" and “0” for "false". The meaning of the content is important for meaningful answers. - **different meanings**

### 🧩 Challenge 2️⃣: Spatial Relationships and Connectivity between Real Things

Geo databases have special features that are used by Digital Twins: **spatial query and spatial join**

**spatial query** uses topological relationships betweeen objects "Which buildings touches the building in Baker Street 221b?"

**spatial join** combines two datasets with rows being matched based on a desired topological relationship, rather than using a stored values as in a normal table join in a relational database.
 "How many buildings are in the boundary of Westminster?"

### 🧩 Challenge 3️⃣: Databases with Many Tables

The **database of a digital twin** usually consists of **many tables**. Often there are **hundreds** or **thousands**. 

Since the **query** to the LLM is **limited in size**, it is not possible to provide a description of all tables. The **LLM** therefore does not know **which tables are available**


```python

```
