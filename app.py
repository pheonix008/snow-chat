import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Chat with Snowflake", page_icon="❄️")
st.title("❄️ Chat with your Sales Data")

# 1. Setup the Database and AI Connections
conn = st.connection("snowflake")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Define the Database Schema for the AI
# The AI needs to know your tables and columns so it can write correct SQL.
DATABASE_SCHEMA = """
You are a Snowflake SQL expert. Write a SQL query to answer the user's question.
Return ONLY the SQL query, no explanations, no markdown formatting.

Here is the database schema:
Table: products (product_id INT, product_name VARCHAR, category VARCHAR, price DECIMAL)
Table: stores (store_id INT, city VARCHAR, region VARCHAR)
Table: sales (sale_id INT, sale_date DATE, product_id INT, store_id INT, quantity INT, total_amount DECIMAL)
"""

# 3. Create the Chat UI
if prompt := st.chat_input("Ask a question (e.g., 'What were the total sales in Paris?')"):
    
    # Display the user's question on screen
    st.chat_message("user").write(prompt)
    
    # 4. Generate the SQL using Gemini
    with st.spinner("Thinking..."):
        # Combine the instructions with the user's question
        full_prompt = f"{DATABASE_SCHEMA}\n\nUser Question: {prompt}"
        
        response = model.generate_content(full_prompt)
        raw_sql = response.text
        
        # Clean up the output in case the AI added formatting like ```sql
        clean_sql = raw_sql.replace("```sql", "").replace("```", "").strip()
        
    # Display the generated SQL (Great for debugging!)
    st.chat_message("ai").write(f"**Generated SQL:**\n```sql\n{clean_sql}\n```")
    
    # 5. Execute the query in Snowflake
    try:
        df = conn.query(clean_sql)
        # Display the results as a table
        st.chat_message("ai").dataframe(df)
    except Exception as e:
        st.error(f"Snowflake couldn't run this query. Error: {e}")