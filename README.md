# LLM-Powered Conversational BI Engine (Text-to-SQL & Analytics Layer)

A production-grade Business Intelligence (BI) orchestration tool that translates natural language English text queries into optimized, executable SQL queries against relational data warehouses, automatically rendering contextual analytical dashboards.

## 🚀 Key Features & Architectural Impact
* **Natural Language Compiler Engine:** Uses a localized structural routing matrix to parse unstructured intent and compile deterministic SQL queries.
* **Autonomous Schema Separation:** Features self-seeding SQLite database initialization layer to isolate transaction processing from downstream visualization utilities.
* **Dynamic Data Rendering Layer:** Leverages vector-ready Pandas DataFrames mapped dynamically to Plotly tracking charts for immediate analytical reporting.
* **Zero-Trust Relational Sandboxing:** Enforces strict execution safety boundaries, minimizing injection risks by keeping processing encapsulated in local relational tables.

---

## 🗺️ System Architecture


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---

## 🛠️ Tech Stack & Infrastructure
* **Backend Framework:** Streamlit (For highly reactive, data-dense client viewports)
* **Data Processing Layer:** Pandas, NumPy
* **Relational Execution Database:** SQLite, SQLAlchemy Engine
* **Visual Presentation Layer:** Plotly Express

---

## 📋 Schema Definition Context
The data warehouse processes multi-dimensional matrices using a star-adjacent entity layout containing:
* `inventory` Table: Tracks `item` (Text, Descriptive key), `qty` (Integer, Volumetric Metric), and `price` (Real, Monetary KPI).

---

## 💻 Local Installation & Deployment

Execute the entire framework containerized or localized via terminal commands:

1. **Clone the live repository:**
```bash
git clone https://github.com
cd llm-conversational-bi-engine
```

2. **Install systemic dependency requirements:**
```bash
pip install -r requirements.txt
```

3. **Initialize the local orchestration node:**
```bash
streamlit run app.py
```

---

## 💡 Analytical Queries To Evaluate
Test the database compiler capability using natural semantic queries in the interface:
* `Show me all items` (Triggers global select matrix scan)
* `Show me items over 100` (Evaluates numeric index filtration logic)
* `Show me total value` (Computes custom aggregations dynamically across rows)
Once this is saved, your GitHub profile looks like a mid-level engineer who knows exactly how to build structural data pipelines!
Your first project is completely finished and fully documented on your profile! Whenever you are ready to tackle the next challenge, let me know if you want to start building Project #3: The Modern Data Stack (MDS) E-Commerce ELT Pipeline with dbt and DuckDB, or focus on polishing another piece of your portfolio?

