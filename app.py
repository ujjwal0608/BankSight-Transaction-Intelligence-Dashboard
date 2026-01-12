import streamlit as st
from streamlit_option_menu import option_menu

# Connecting to mysql 
import mysql.connector
import pandas as pd

@st.cache_resource
def get_connection():
    return mysql.connector.connect(
    host = '127.0.01',
    user = 'root',
    password = 'Ujjwal@0608',
    database = 'BankData',
    use_pure = True
    )

def get_primary_key(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
    pk = cursor.fetchone()[4]
    cursor.close()
    return pk

def get_columns(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    column = cursor.fetchall()
    cursor.close()
    return column
    

st.set_page_config(layout = 'wide')

# Use of CSS for Better Visuals 

st.markdown('''
    <style>
    section[data-testid = 'stSidebar']{
        width : 380px !important;
    }
    section[data-testid = 'stSidebar'] > div{
        width : 380px !important;
    }
    </style>
    ''',
    unsafe_allow_html = True
)

# SideBox
with st.sidebar:
    select = option_menu(
        menu_title = 'BankSight Navigation',
        options = ['Introduction', 'View Table', 'Filter Data', 'CRUD Operation', 'Credit/Debit Simulation', 'Analytical Insight', 'About Creator'],
        icons =['house', 'bar-chart', 'search', 'pencil', 'cash-coin', 'cpu', 'folder'],
        menu_icon = 'bank',
        default_index = 0
    )
    
# Page 1 Start
if select == 'Introduction':
    st.title('🏦 BankSight : Transaction Intelligence Dashboard')
    st.subheader('Project Overview')
    st.markdown('''
    **BankSight** is a financial analytics system built using **Python, Streamlit, and SQLite**.
    It allows user to explor Cutomers, Accounts, Transactions, Loans, and Support Data perform 
    CRUD operations, simulate deposit and withdrawls, and gain actionable insights.
    ''')
    st.subheader('Objective')
    st.markdown('''
    <ul>
    <li> Understand customer and Transaction behaviour </li>  
    <li> Detect anomalies and potential fraud</li>
    <li> Enable CRUD Operation in all dataset</li>
    <li>  Simulate Banking Transaction (Credit/Debit)</li>
    </ul>
    ''',unsafe_allow_html = True)
    
# Page 2 Started
elif select == 'View Table':
    st.title('📊 View Database Tables')
    
    conn = get_connection()
    table_name = st.selectbox(
        'Select a Table',
        ['Customers', 'Accounts', 'Transactions', 'Loans', 'Credit_Cards', 'Branchs', 'Support_Tickets']
    )
    
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    
    st.dataframe(df, use_container_width = True)
# Page 3 Started
elif select == 'Filter Data':
    st.title('🔍 Filter Data')
    
    conn = get_connection()
    # Selecting the table 
    table_name = st.selectbox(
    'Select Table To Filter',
    ['Customers', 'Accounts', 'Transactions', 'Loans', 'Credit_Cards', 'Branchs', 'Support_Tickets']
    )
    # Loading the Table
    df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
    st.markdown('### Select column and values to filter:')
    #Creating a filter 
    
    filters = {}
    for col in df.columns:
        unique_values = df[col].dropna().unique()
        
        selected_values = st.multiselect(
            label = f'{col}:',
            options = sorted(map(str, unique_values)),
            placeholder = 'Choose an option'
        )
        if selected_values:
            filters[col] = selected_values
    
    filtered_df = df.copy()
    for col, values in filters.items():
        filtered_df = filtered_df[
            filtered_df[col].astype(str).isin(values)
        ]
    # Sucess Message
    if filters:
        st.success("Data Filtered Sucessfully")
        
    st.dataframe(filtered_df, use_container_width = True)
    
# Page 3 Started   
elif select == 'CRUD Operation':
    st.title('✏️ CRUD Operation')
    conn = get_connection()
    table_name = st.selectbox(
        'Select Table',
        ['Customers', 'Accounts', 'Transactions', 'Loans', 'Credit_Cards', 'Branchs', 'Support_Tickets'] 
    )
    operation = st.radio(
        'Select Operation',
        ['View', 'Add', 'Update', 'Delete']
    )
    pk = get_primary_key(table_name)
    columns = get_columns(table_name)
    column_name = [col[0] for col in columns]
    
    
    if operation == 'View':
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        st.dataframe(df, use_container_width = True)
        
    elif operation == 'Add':
        st.subheader(f'+ Add New Record To {table_name}')
        
        input_data = {}
        
        for col, dtype, *_ in columns:
            if 'date' in col.lower():
                input_data[col] = st.date_input(f'Enter {col}')
            else:
                input_data[col] = st.text_input(f'Enter {col}')
                
        if st.button('Insert Record'):
            placeholders = ",".join(["%s"] * len(input_data))
            col_name = ",".join(input_data.keys())
            
            query = f"INSERT INTO {table_name} ({col_name}) VALUES ({placeholders})"
            
            cursor = conn.cursor()
            cursor.execute(query, tuple(input_data.values()))
            conn.commit()

            
            st.success('Record Inserted Successfully!')
        
    elif operation == 'Update':
        st.subheader(f'Update Records in {table_name}')
        
        df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
        
        selected_pk = st.selectbox(
            f'Select {pk} to Update',
            df[pk].astype(str).unique()
        )
        column_to_update = st.selectbox(
            'Select Column to Update',
            column_name
        )
        new_value = st.text_input('Enter the New Value')
        
        if st.button('Update Records'):
            query = f"""
            UPDATE {table_name}
            SET {column_to_update} = %s
            WHERE {pk} = %s
            """
            
            cursor = conn.cursor()
            cursor.execute(query, (new_value, selected_pk))
            conn.commit()

            
            st.success('Record updated successfully!')
            
    elif operation == 'Delete':
        st.subheader(f'🗑️ Delete Record from {table_name}')
            
        df = pd.read_sql(f'SELECT * FROM {table_name}', conn)
            
        delete_pk = st.selectbox(
            f'Select {pk} to Delete',
            df[pk].astype(str).unique()
        )
            
        confirm = st.checkbox('I confirm I want to Delete this Record')
            
        if st.button('Delete Record') and confirm:
            query = f'DELETE FROM {table_name} WHERE {pk} = %s'
                
            cursor = conn.cursor()
            cursor.execute(query, (delete_pk,))
            conn.commit()
            
                
            st.success('Record Deleted Successfully')
            
# Page 4 Started
elif select == 'Credit/Debit Simulation':
    st.subheader('💰Credit/Debit Simulation')
    conn = get_connection()
    cursor = conn.cursor()
    
    account_id = st.text_input('Enter Account id')
    amount = st.number_input('Enter Amount', min_value = 0.0, step = 100.0)
    
    action = st.radio(
        'Select Action',
        ['Check Balance', 'Deposit', 'WithDrawl']
    )
    if st.button('Submit'):
        
        cursor.execute(
            "SELECT account_balance FROM Accounts WHERE customer_id = %s",
            (account_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            st.error('❌ Account ID Not Found')

            st.stop()
        current_balance = float(result[0])
        
        if action == 'Check Balance':
            st.success(f"Current Balance: ₹{current_balance: .2f}")
            
        elif action == 'Deposit':
            if amount <= 0:
                st.warning('⚠️ Enter a Valid Amount')
            else:
                new_balance = current_balance + amount
                cursor.execute(
                    "UPDATE Accounts SET account_balance = %s WHERE customer_id = %s",
                    (new_balance, account_id)
                )
                conn.commit()
                st.success(f'✅ Deposit Successful! New Balance: ₹{new_balance: .2f}')
                
        elif action == 'WithDrawl':
            if amount <= 0:
                st.warning('⚠️ Enter a Valid Amount')
            elif current_balance - amount <1000:
                st.error('❌ Minimum Balance 1000 must be maintained')
            else:
                new_balance = current_balance - amount
                cursor.execute(
                    'UPDATE Accounts SET account_balance = %s WHERE customer_id = %s',
                    (new_balance, account_id)
                )
                conn.commit()
                st.success(f"✅ Withdrawl Successful! New Balance: ₹{new_balance: .2f}")
                
        
                
    
    
    
    
elif select == 'Analytical Insight':
    st.title("🧠 Analytical Insights")

    conn = get_connection()

    insights = {
        "Q1: Customers per city & average account balance": """
            SELECT 
                c.city,
                COUNT(DISTINCT(c.customer_id)) as Total_Customer,
                AVG(a.account_balance) as AVG_Account_Balance
                FROM Customers as c
            JOIN Accounts as a
                ON c.customer_id = a.customer_id
            GROUP BY c.city

        """,

        "Q2: Account type with highest total balance": """
            SELECT 
                account_type,
                SUM(account_balance) as Total_Balance
            FROM Customers as c
            JOIN Accounts as a
                  ON c.customer_id = a.customer_id
            GROUP BY account_type
        """,

        "Q3: Top 10 customers by total account balance": """
            SELECT
                c.customer_id,
                c.name,
                SUM(account_balance) as total_balance
            FROM Customers as c
            JOIN Accounts as a 
                ON c.customer_id = a.customer_id
            GROUP BY c.customer_id, c.city
            ORDER BY a.account_balance desc
            LIMIT 10
        """,

        "Q4: Customers who opened accounts in 2023 with balance > ₹1,00,000": """
            SELECT 
                c.customer_id,
                c.name,
                a.account_balance,
                c.join_date
            FROM Customers as c
            JOIN Accounts as a 
                ON c.customer_id = a.customer_id
            WHERE YEAR(c.join_date) = 2023 
            AND a.account_balance > 100000;
        """,

        "Q5: Total transaction volume by transaction type": """
            SELECT
                txn_type,
                SUM(amount) AS Total_amount
            FROM Transactions
            GROUP BY txn_type 
            ORDER BY Total_amount DESC
        """,

        "Q6: Failed transactions per transaction type": """
            SELECT 
                txn_type as Transaction_Type,
                COUNT(*) as Failed_Transactions
            FROM Transactions
            WHERE status = 'failed'
            GROUP BY txn_type;
        """,

        "Q7: Total number of transactions per type": """
            SELECT transaction_type,
                   COUNT(*) AS total_transactions
            FROM Transactions
            GROUP BY transaction_type
        """,

        "Q8: Accounts with ≥5 transactions above ₹20,000": """
            SELECT
                customer_id,
                count(*) as High_Transactions
            FROM Transactions
            WHERE amount > 20000
            GROUP BY customer_id
            HAVING COUNT(*) >= 5
        """,

        "Q9: Average loan amount & interest rate by loan type": """
            SELECT
                Loan_Type,
                avg(Loan_Amount) as Average_Amount,
                avg(Interest_Rate) as Average_Interest
            FROM Loans
            GROUP BY Loan_Type
        """,

        "Q10: Customers with more than one active/approved loan": """
            SELECT 
                Customer_ID,
                COUNT(*) as Active_loan
            FROM Loans
            WHERE Loan_Status in ('Active', 'Approved')
            GROUP BY Customer_ID
            HAVING COUNT(*) > 1;
        """,

        "Q11: Top 5 customers with highest outstanding loan amounts": """
            SELECT customer_id,
                   SUM(loan_amount) AS outstanding_amount
            FROM Loans
            WHERE loan_status != 'Closed'
            GROUP BY customer_id
            ORDER BY outstanding_amount DESC
            LIMIT 5
        """,

        "Q12: Average loan amount per branch": """
            SELECT Branch,
                   ROUND(AVG(Loan_Amount), 2) AS Avg_loan_amount
            FROM Loans
            GROUP BY Branch
        """,

        "Q13: Customers per age group": """
            SELECT
                CASE
                    WHEN age BETWEEN 18 AND 25 THEN '18–25'
                    WHEN age BETWEEN 26 AND 35 THEN '26–35'
                    WHEN age BETWEEN 36 AND 50 THEN '36–50'
                    ELSE '50+'
                END AS age_group,
                COUNT(*) AS customer_count
            FROM Customers
            GROUP BY age_group
        """,

        "Q14: Issue categories with longest average resolution time": """
            SELECT issue_category,
                   ROUND(AVG(DATEDIFF(date_closed, date_opened)), 2) AS avg_resolution_days
            FROM Support_Tickets
            WHERE date_closed IS NOT NULL
            GROUP BY issue_category
            ORDER BY avg_resolution_days DESC
        """,

        "Q15: Support agents resolving most critical tickets (rating ≥ 4)": """
            SELECT support_agent,
                   COUNT(*) AS resolved_tickets
            FROM Support_Tickets
            WHERE priority = 'Critical'
              AND customer_rating >= 4
            GROUP BY support_agent
            ORDER BY resolved_tickets DESC
        """
    }

    selected_question = st.selectbox(
        "Select an analytical question",
        list(insights.keys())
    )

    sql_query = insights[selected_question]

    st.markdown("### 🧾 SQL Query Used")
    st.code(sql_query, language="sql")

    df = pd.read_sql(sql_query, conn)

    st.markdown("### 📊 Result")
    st.dataframe(df, use_container_width=True)
    
    
# Last page 
elif select == 'About Creator':

    st.title("👩‍💻 About the Creator")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Profile Photo")
        st.image('/Users/ujjwalraj/Desktop/IMG_1973.png', width=200)

    with col2:
        st.markdown("## Ujjwal Raj")
        st.markdown("### Aspiring Data Scientist")

        st.markdown("""
        I am a **fresher aspiring Data Scientist** with a strong foundation in data analysis, 
        machine learning, and data-driven application development.  
        
        I am actively seeking opportunities to **start my career as a Data Scientist**, where I can 
        apply my analytical skills, problem-solving mindset, and passion for learning to solve 
        real-world business problems—especially in domains like **banking and finance**.
        """)

    st.divider()

 
    st.subheader("🛠️ Technical Expertise")

    st.markdown("""
    - **Programming & DSA:** Python  
    - **Databases & SQL:** MySQL, SQLite, Query Optimization  
    - **Data Analysis:** EDA, Data Cleaning, Feature Engineering  
    - **Machine Learning:** Regression, Classification, Clustering  
    - **Deep Learning:** Neural Networks, CNNs  
    - **Computer Vision:** Image Processing, Model Building  
    - **NLP:** Text Processing, Tokenization, ML-based NLP  
    - **Data Engineering:** ETL Concepts, Data Pipelines  
    - **Deployment & Apps:** Streamlit  
    - **Cloud Basics:** AWS  
    """)

    st.divider()


    st.subheader("📊 Project Focus")

    st.markdown("""
    **BankSight – Transaction Intelligence Dashboard**

    - End-to-end data analytics project using **Python, SQL, and Streamlit**
    - Implements **CRUD operations**, **transaction simulations**, and **analytical insights**
    - Uses **real-world banking datasets** to answer business-driven questions
    - Designed with **scalability, transparency, and usability** in mind
    """)

    st.divider()


    st.subheader("📬 Contact Information")

    st.markdown("""
    <ul>
    <li>📧 **Email : ujjwalraj6aug@gmail.com</li>
    <li>💼 **LinkedIn : www.linkedin.com/in/ujjwalraj06</li>  
    </ul>
    """, unsafe_allow_html = True)

    st.caption("🚀 Open to Data Scientist/ML Engineer entry-level opportunities")
