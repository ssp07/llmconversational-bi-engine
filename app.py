import os
import sqlite3
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import re

# ==========================================
# 1. DATABASE CONNECTIVITY & NORMALIZATION
# ==========================================
DB_FILE = "bi_data.db"
engine = create_engine(f"sqlite:///{DB_FILE}")

def load_dataset():
    if os.path.exists("dataset.csv"):
        df = pd.read_csv("dataset.csv")
        # Strip all whitespace, convert to lowercase, replace special chars with underscores
        df.columns = [c.strip().lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "") for c in df.columns]
        df.to_sql("analytics_table", engine, if_exists="replace", index=False)
        return "analytics_table"
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS inventory")
    c.execute("CREATE TABLE inventory (item TEXT, qty INTEGER, price REAL)")
    c.executemany("INSERT INTO inventory VALUES (?,?,?)", [
        ('laptop', 15, 999.99), ('mouse', 120, 25.50), ('monitor', 30, 299.00)
    ])
    conn.commit()
    conn.close()
    return "inventory"

active_table = load_dataset()

# ==========================================
# 2. STREAMLIT Front-End Setup
# ==========================================
st.set_page_config(page_title="Conversational BI Engine", layout="wide")
st.title(" 🚀 Enterprise Conversational BI Engine & Strategy Matrix")
st.markdown("---")

conn = sqlite3.connect(DB_FILE)
df_schema = pd.read_sql_query(f"SELECT * FROM {active_table} LIMIT 1", conn)
conn.close()

# Dynamic dataset-aware FAQ matrix generation
is_ecommerce = "visit_duration" in df_schema.columns or "n_products_viewed" in df_schema.columns

if is_ecommerce:
    faq_registry = {
        "Select a pre-verified question...": None,
        "Q1: Show me all user tracking logs inside the table": f"SELECT * FROM {active_table};",
        "Q2: Show me items where visit duration is over 0.5 seconds": f"SELECT * FROM {active_table} WHERE visit_duration > 0.5;",
        "Q3: Show me items where the product view count is over 3": f"SELECT * FROM {active_table} WHERE n_products_viewed > 3;",
        "Q6: Isolate traffic metrics exclusively for mobile device users": f"SELECT * FROM {active_table} WHERE is_mobile = 1;",
        "Q9: Sort all records dynamically based on the longest session visit duration": f"SELECT * FROM {active_table} ORDER BY visit_duration DESC;"
    }
else:
    first_col = df_schema.columns[0] if len(df_schema.columns) > 0 else "id"
    last_col = df_schema.columns[-1] if len(df_schema.columns) > 0 else "value"
    faq_registry = {
        "Select a pre-verified question...": None,
        f"Q1: Show me a complete view of all records inside the active {active_table} table": f"SELECT * FROM {active_table};",
        f"Q2: Sort rows based on the first column ({first_col})": f"SELECT * FROM {active_table} ORDER BY {first_col} ASC;",
        f"Q3: Rank the highest recorded tracking metrics grouped by ({last_col})": f"SELECT * FROM {active_table} ORDER BY {last_col} DESC;"
    }

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("💡 Option A: Pre-Verified Dropdown Selector")
    selected_faq = st.selectbox("Choose a query to execute instantly:", list(faq_registry.keys()))

with col_right:
    st.subheader("💬 Option B: Custom Text Search Bar")
    user_input = st.text_input("Type your question manually (e.g., 'show all logs'):", "")

# ==========================================
# 3. HIGH-PERFORMANCE INTENT PARSER
# ==========================================
def parse_manual_input(text_in):
    if not text_in:
        return None, True
    clean_input = text_in.lower().strip()
    columns_str = ", ".join(df_schema.columns)
    
    schema_columns = df_schema.columns.tolist()
    has_column_intent = any(col in clean_input for col in schema_columns)
    has_global_intent = any(word in clean_input for word in ["everything", "all", "show", "select", "logs", "table"])
    
    if not (has_column_intent or has_global_intent):
        return None, False
        
    where_clauses = []
    
    vd_check = re.search(r"visit_duration\s+(?:over|greater\s+than|>)\s*(\d+(?:\.\d+)?)", clean_input)
    if "visit_duration" in clean_input and vd_check:
        where_clauses.append(f"visit_duration > {float(vd_check.group(1))}")
        
    np_check = re.search(r"n_products_viewed\s+(?:over|greater\s+than|>)\s*(\d+)", clean_input)
    if "n_products_viewed" in clean_input and np_check:
        where_clauses.append(f"n_products_viewed > {int(np_check.group(1))}")

    if "is_mobile" in clean_input or "mobile" in clean_input:
        if "1" in clean_input or "true" in clean_input or "yes" in clean_input:
            where_clauses.append("is_mobile = 1")
        elif "0" in clean_input or "false" in clean_input or "no" in clean_input:
            where_clauses.append("is_mobile = 0")
            
    order_clause = ""
    for col in df_schema.columns:
        if any(sort_term in clean_input for sort_term in ["order by", "ordered by", "sort by"]):
            if col in clean_input:
                order_clause = f" ORDER BY {col} DESC"
                break
    
    final_query = f"SELECT {columns_str} FROM {active_table}"
    if where_clauses:
        final_query += " WHERE " + " AND ".join(where_clauses)
    final_query += order_clause + ";"
    return final_query, True

q_dropdown = faq_registry[selected_faq] if selected_faq != "Select a pre-verified question..." else None
q_manual, is_manual_valid = parse_manual_input(user_input)

# ==========================================
# 4. DATA TRANSFORMATION & EXECUTOR
# ==========================================
if q_dropdown or q_manual:
    st.markdown("---")
    
    if q_dropdown and q_manual:
        st.subheader("🏁 Multi-Query Comparison View")
        tab1, tab2 = st.tabs(["📌 Query 1: Dropdown Selection", "📝 Query 2: Manual Text Request"])
        queries_to_run = [(tab1, q_dropdown, "Dropdown View"), (tab2, q_manual, "Manual Text View")]
    elif q_manual:
        if not is_manual_valid:
            st.error("❌ Couldn't interpret the query context. Please enter a valid data request relating to active schema columns.")
            queries_to_run = []
        else:
            queries_to_run = [(st, q_manual, "Manual Text Request Summary")]
    else:
        queries_to_run = [(st, q_dropdown, "Dropdown Selection Summary")]

    for container, target_query, label_text in queries_to_run:
        df_results = pd.DataFrame()
        try:
            df_results = pd.read_sql_query(target_query, engine)
        except Exception as query_err:
            container.error(f"Processing Error on pipeline node: {query_err}")
            
        if not df_results.empty:
            container.success(f"Executed SQL Expression ({label_text}): `{target_query}`")
            
            # Safe calculation parameters with zero column dependency crashes
            total_rows = len(df_results)
            avg_duration = df_results["visit_duration"].mean() if "visit_duration" in df_results.columns else 0
            avg_views = df_results["n_products_viewed"].mean() if "n_products_viewed" in df_results.columns else 0
            mobile_pct = (df_results["is_mobile"] == 1).sum() / total_rows * 100 if "is_mobile" in df_results.columns else 0
            conversion_rate = (df_results["user_action"] == 1).sum() / total_rows * 100 if "user_action" in df_results.columns else 0

            # 📝 Strategy Bullet Summary
            container.markdown("### 🎯 Executive Data Trend Summary")
            container.info(f"""
* **💎 Segment Density:** Identified **{total_rows} matching data records** inside this specific dataset slice.
* **⚡ Funnel Browse Velocity:** Active users average a browse window of **{avg_duration:.2f} seconds** and scan **{avg_views:.1f} items**.
* **📱 Funnel Channel Allocation:** **{mobile_pct:.1f}%** of this traffic profile originated directly via mobile device configurations.
* **🎯 Bottom-Line Conversion Rate:** The exact click-to-action conversion rate parameter for this segment layer is sitting explicitly at **{conversion_rate:.1f}%**.
            """)
            
            container.markdown("### 📋 Filtered Data Grid Table")
            container.dataframe(df_results.head(100), use_container_width=True, hide_index=True)
            
            # ==========================================
            # 🌟 AUTOMATIC BROAD DYNAMIC COLUMN RESOLVER (FIXES BLANK SCREEN CRASHES)
            # ==========================================
            container.markdown("### 📈 Strategic Trend-Highlighted Visual Charts")
            
            # Explicitly find any numeric column inside the active dataframe to use for mapping charts
            numeric_cols = df_results.select_dtypes(include=[np.number]).columns.tolist()
            text_cols = df_results.select_dtypes(include=[object]).columns.tolist()
            
            # Establish fallback variables if exact e-commerce metrics aren't matching
            y_axis = "visit_duration" if "visit_duration" in numeric_cols else (numeric_cols[-1] if numeric_cols else df_results.columns[-1])
            x_axis = "n_products_viewed" if "n_products_viewed" in numeric_cols else (numeric_cols[0] if len(numeric_cols) > 1 else df_results.columns[0])
            
            # Ensure a clean shallow object frame copy is formatted as numbers explicitly
            df_chart = df_results.head(100).copy().reset_index(drop=True)
            df_chart[x_axis] = pd.to_numeric(df_chart[x_axis], errors='coerce').fillna(0)
            df_chart[y_axis] = pd.to_numeric(df_chart[y_axis], errors='coerce').fillna(0)
            
            # Build Side-By-Side Visual Display Sub-Grids
            g_col1, g_col2 = container.columns(2)
            
            with g_col1:
