import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. Create a quick, free internal database automatically
DB_FILE = "bi_data.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

def run_db_setup():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS inventory (item TEXT, qty INTEGER, price REAL)")
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone() == 0:
        c.executemany("INSERT INTO inventory VALUES (?,?,?)", [
            ('Laptop', 15, 999.99), ('Mouse', 120, 25.50), ('Monitor', 30, 299.00)
        ])
        conn.commit()
    conn.close()
run_db_setup()

# 2. UI Layout Screen
st.title("🤖 Text-To-SQL Conversational BI Engine")
st.markdown("### Enterprise Data Analytics Dashboard")

# Interactive Sidebar to help recruiters
with st.sidebar:
    st.markdown("### 🗄️ Database Schema")
    st.markdown("**Table:** `inventory`")
    st.markdown("**Columns:** `item` (Text), `qty` (Integer), `price` (Real)")
    st.markdown("---")
    st.markdown("💡 **Try these queries:**")
    st.code("Show me all items")
    st.code("Show me items over 100")

user_input = st.text_input("💬 Ask your database a business question in plain English:", "")

# 3. Rule-Based Text-to-SQL Compiler Matrix
if user_input:
    clean_input = user_input.lower().strip()
    
    # Custom query matching matrix logic
    if "over 100" in clean_input or "> 100" in clean_input:
        sql_query = "SELECT item, qty, price FROM inventory WHERE price > 100;"
    elif "qty" in clean_input or "quantity" in clean_input:
        sql_query = "SELECT item, qty FROM inventory ORDER BY qty DESC;"
    elif "total value" in clean_input or "revenue" in clean_input:
        sql_query = "SELECT item, (qty * price) AS total_value FROM inventory;"
    else:
        sql_query = "SELECT item, qty, price FROM inventory;"
        
    st.subheader("🛠️ Synthesized SQL Query Generated")
    st.code(sql_query, language="sql")
    
    # Run the SQL query against our data and display it
    try:
        df = pd.read_sql_query(sql_query, engine)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Executed Data Result")
            st.dataframe(df, use_container_width=True)
        with col2:
            st.subheader("📈 Automated Dynamic Chart")
            if not df.empty and 'item' in df.columns:
                y_axis = df.columns[-1]
                fig = px.bar(df, x='item', y=y_axis, title=f"{y_axis} by Item", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error executing query: {e}") 

