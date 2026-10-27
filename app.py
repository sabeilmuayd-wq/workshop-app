import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    # جدول التكاليف
    c.execute('''CREATE TABLE IF NOT EXISTS costs
                 (id INTEGER PRIMARY KEY, item TEXT, amount REAL, entry_date TEXT)''')
    # جدول المبيعات
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY, product TEXT, qty INTEGER, unit_price REAL, total REAL, entry_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- دوال مساعدة ---
def add_cost(item, amount):
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute("INSERT INTO costs (item, amount, entry_date) VALUES (?, ?, ?)", (item, amount, str(date.today())))
    conn.commit()
    conn.close()

def add_sale(product, qty, unit_price):
    total = qty * unit_price
    conn = sqlite3.connect('workshop.db')
    c = conn.cursor()
    c.execute("INSERT INTO sales (product, qty, unit_price, total, entry_date) VALUES (?, ?, ?, ?, ?)", 
              (product, qty, unit_price, total, str(date.today())))
    conn.commit()
    conn.close()

def get_data(table):
    conn = sqlite3.connect('workshop.db')
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

# --- واجهة التطبيق ---
st.set_page_config(page_title="ورشة مؤيد", page_icon="🪚", layout="centered")

st.title("🪚 إدارة ورشة النجارة")
st.markdown("---")

# --- التبويبات ---
tab1, tab2, tab3 = st.tabs(["📉 تسجيل التكاليف", "💰 تسجيل المبيعات", "📊 التقرير المالي"])

with tab1:
    st.header("إضافة تكلفة جديدة")
    with st.form("cost_form", clear_on_submit=True):
        item = st.text_input("اسم المادة (مثال: خشب، دهان، مسامير)")
        amount = st.number_input("السعر", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("إضافة التكلفة")
        if submitted and item and amount > 0:
            add_cost(item, amount)
            st.success(f"تم إضافة: {item} بمبلغ {amount}")
            st.rerun()

with tab2:
    st.header("إضافة عملية بيع")
    with st.form("sale_form", clear_on_submit=True):
        product = st.text_input("اسم المنتج (مثال: فرمة)")
        qty = st.number_input("الكمية", min_value=1, step=1)
        unit_price = st.number_input("سعر البيع للواحد", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("إضافة البيع")
        if submitted and product and qty > 0 and unit_price > 0:
            add_sale(product, qty, unit_price)
            st.success(f"تم تسجيل بيع {qty} {product} بقيمة إجمالية {qty * unit_price}")
            st.rerun()

with tab3:
    st.header("التقرير المالي")
    
    costs_df = get_data('costs')
    sales_df = get_data('sales')
    
    total_costs = costs_df['amount'].sum() if not costs_df.empty else 0.0
    total_sales = sales_df['total'].sum() if not sales_df.empty else 0.0
    profit = total_sales - total_costs
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي التكاليف", f"{total_costs:,.0f}")
    col2.metric("إجمالي المبيعات", f"{total_sales:,.0f}")
    col3.metric("صافي الربح", f"{profit:,.0f}", delta=f"{profit:,.0f}")
    
    st.markdown("---")
    st.subheader("سجل التكاليف")
    st.dataframe(costs_df, use_container_width=True)
    
    st.subheader("سجل المبيعات")
    st.dataframe(sales_df, use_container_width=True)
