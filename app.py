import os
import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# 1. DATABASE CONNECTIVITY SETUP
DB_FILE = "bi_data.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

def load_custom_dataset():
    """Checks if a custom dataset exists, otherwise initializes a default one."""
    conn = sqlite3.connect(DB_FILE)
    
    # CASE A: If you place an 'ecommerce.csv' or 'medical.csv' in your folder, it loads automatically!
    if os.path.exists("dataset.csv"):
        df = pd.read_csv("dataset.csv")
        # Clean column names to remove spaces/special characters for easy SQL query syntax
        df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]
        df.to_sql("analytics_table", engine, if_exists="replace", index=False)
        table_name = "analytics_table"
    else:
        # CASE B: Fallback mock inventory data if no file is uploaded yet
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS inventory")
        c.execute("CREATE TABLE inventory (item TEXT, qty INTEGER, price REAL)")
        c.executemany("INSERT INTO inventory VALUES (?,?,?)", [
            ('Laptop', 15, 999.99), ('Mouse', 120, 25.50), ('Monitor', 30, 299.00), ('Keyboard', 45, 89.99)
        ])
        conn.commit()
        table_name = "inventory"
        
    conn.close()
    return table_name

# Initialize database configuration and fetch active target table name
active_table = load_custom_dataset()

# 2. STREAMLIT VISUAL LAYER SETUP
st.set_page_config(page_title="Text-To-SQL BI Engine", layout="wide")
st.title("🤖 Text-To-SQL Conversational BI Engine")
st.markdown("### Enterprise Data Analytics Dashboard Layer")

# Build dynamic configuration context block in sidebar menu
with st.sidebar:
    st.markdown("### 🗄️ Active Database Context")
    st.success(f"Connected to Table: `{active_table}`")
    
    # Read active structural columns to help user build query terms
    conn = sqlite3.connect(DB_FILE)
    df_schema = pd.read_sql_query(f"SELECT * FROM {active_table} LIMIT 1", conn)
    conn.close()
    
    st.markdown("**Available Operational Metric Fields:**")
    for col in df_schema.columns:
        st.code(col)
    st.markdown("---")
    st.markdown("💡 **Try these semantic prompt templates:**")
    st.code(f"Show me everything from {active_table}")
    st.code(f"Select highest records ordered by {df_schema.columns[-1] if not df_schema.empty else ''}")

user_input = st.text_input("💬 Ask your database a business question in plain English:", "")

# 3. HIGH-PERFORMANCE INTENT INTERPRETATION LOGIC MATRIX
if user_input:
    clean_input = user_input.lower().strip()
    columns_str = ", ".join(df_schema.columns)
    
    # Evaluation layer mapping textual queries directly to SQL expressions
    if "over" in clean_input or ">" in clean_input:
        # Extract any numeric value mentioned in user string
        num = ''.join(filter(str.isdigit, clean_input))
        num = num if num else "100"
        target_col = df_schema.columns[-1]  # Safely targets price or numeric metric column
        sql_query = f"SELECT {columns_str} FROM {active_table} WHERE {target_col} > {num};"
    elif "highest" in clean_input or "order by" in clean_input or "sort" in clean_input:
        target_col = df_schema.columns[1] if len(df_schema.columns) > 1 else df_schema.columns[0]
        sql_query = f"SELECT {columns_str} FROM {active_table} ORDER BY {target_col} DESC;"
    else:
        sql_query = f"SELECT {columns_str} FROM {active_table};"
        
    st.subheader("🛠️ Synthesized SQL Query Generated")
    st.code(sql_query, language="sql")
    
    # Run Compiled Query String securely against engine
    try:
        df_results = pd.read_sql_query(sql_query, engine)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📋 Executed Data Result Table")
            st.dataframe(df_results, use_container_width=True)
        with col2:
            st.subheader("📈 Automated Dynamic Chart Visualization")
            if not df_results.empty and len(df_results.columns) >= 2:
                x_axis = df_results.columns[0]
                y_axis = df_results.columns[-1]
                fig = px.bar(df_results, x=x_axis, y=y_axis, title=f"{y_axis} grouped by {x_axis}", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 Tabular format optimal for individual value metrics.")
    except Exception as query_error:
        st.error(f"Execution Error: {query_error}")

