import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Rapid Trading Company ERP", layout="wide")
st.title("Rapid Trading Company - Lights Trading ERP")

purchase_file = "purchase.csv"
sales_file = "sales.csv"

if not os.path.exists(purchase_file):
    pd.DataFrame(columns=["Date", "Party Name", "Product", "Quantity", "Price", "Received By"]).to_csv(purchase_file, index=False)
if not os.path.exists(sales_file):
    pd.DataFrame(columns=["Date", "Party Name", "Product", "Quantity", "Price"]).to_csv(sales_file, index=False)

purchases = pd.read_csv(purchase_file)
sales = pd.read_csv(sales_file)

menu = st.sidebar.radio("Menu", ["Purchase", "Sales", "Reports"])

def safe_filter(df, column, text):
    if text and column in df.columns and not df.empty:
        return df[df[column].fillna("").str.contains(text, case=False, na=False)]
    return df

def safe_date_filter(df, date_col, date_range):
    if date_range and len(date_range) == 2 and date_col in df.columns and not df.empty:
        start, end = date_range
        df = df[
            (pd.to_datetime(df[date_col], errors="coerce") >= pd.to_datetime(start)) &
            (pd.to_datetime(df[date_col], errors="coerce") <= pd.to_datetime(end))
        ]
    return df

# ---------- PURCHASE TAB ---------- #
if menu == "Purchase":
    st.header("Record Purchase Entry")
    with st.form("purchase_form", clear_on_submit=True):
        date = st.date_input("Date", value=datetime.today())
        party = st.text_input("Party Name")
        product = st.text_input("Product")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price per unit (₹)", min_value=0.0, format="%.2f")
        received_by = st.selectbox("Received By", ["Transport", "By Hand", "Courier", "Other"])
        submitted = st.form_submit_button("Add Purchase")

        if submitted:
            new_entry = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"),
                "Party Name": party.strip(),
                "Product": product.strip(),
                "Quantity": quantity,
                "Price": price,
                "Received By": received_by
            }])
            purchases = pd.concat([purchases, new_entry], ignore_index=True)
            purchases.to_csv(purchase_file, index=False)
            st.success(f"Purchase entry added for {product} on {date}")

    st.subheader("Purchase Records: Search & Edit/Delete")
    prod_search = st.text_input("Search Product (Purchase)", key="prod_search_p")
    party_search = st.text_input("Search Party Name (Purchase)", key="party_search_p")
    date_range = st.date_input("Filter by Date Range (Purchase)", [], key="date_search_p")

    filtered_purchase = purchases.copy()
    filtered_purchase = safe_filter(filtered_purchase, 'Product', prod_search)
    filtered_purchase = safe_filter(filtered_purchase, 'Party Name', party_search)
    filtered_purchase = safe_date_filter(filtered_purchase, "Date", date_range)

    edited_purchase = st.data_editor(filtered_purchase, num_rows="dynamic", use_container_width=True)
    if st.button("Save Edited Purchases"):
        for idx in edited_purchase.index:
            purchases.loc[idx] = edited_purchase.loc[idx]
        purchases.to_csv(purchase_file, index=False)
        st.success("Purchases saved.")
        st.experimental_rerun()

    st.write("To delete rows: select row indices below and click 'Delete'")
    delete_p_idx = st.multiselect("Select Purchase Rows to Delete", filtered_purchase.index.tolist())
    if st.button("Delete Selected Purchases"):
        purchases = purchases.drop(delete_p_idx).reset_index(drop=True)
        purchases.to_csv(purchase_file, index=False)
        st.success("Selected purchases deleted.")
        st.experimental_rerun()

# ---------- SALES TAB ---------- #
elif menu == "Sales":
    st.header("Record Sales Entry")
    with st.form("sales_form", clear_on_submit=True):
        date = st.date_input("Date", value=datetime.today())
        party = st.text_input("Party Name")
        product = st.text_input("Product")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        price = st.number_input("Price per unit (₹)", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Add Sale")
        if submitted:
            new_entry = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"),
                "Party Name": party.strip(),
                "Product": product.strip(),
                "Quantity": quantity,
                "Price": price,
            }])
            sales = pd.concat([sales, new_entry], ignore_index=True)
            sales.to_csv(sales_file, index=False)
            st.success(f"Sale entry added for {product} on {date}")

    st.subheader("Sales Records: Search & Edit/Delete")
    prod_search_s = st.text_input("Search Product (Sales)", key="prod_search_s")
    party_search_s = st.text_input("Search Party Name (Sales)", key="party_search_s")
    date_range_s = st.date_input("Filter by Date Range (Sales)", [], key="date_search_s")

    filtered_sales = sales.copy()
    filtered_sales = safe_filter(filtered_sales, 'Product', prod_search_s)
    filtered_sales = safe_filter(filtered_sales, 'Party Name', party_search_s)
    filtered_sales = safe_date_filter(filtered_sales, "Date", date_range_s)

    edited_sales = st.data_editor(filtered_sales, num_rows="dynamic", use_container_width=True)
    if st.button("Save Edited Sales"):
        for idx in edited_sales.index:
            sales.loc[idx] = edited_sales.loc[idx]
        sales.to_csv(sales_file, index=False)
        st.success("Sales saved.")
        st.experimental_rerun()

    st.write("To delete rows: select row indices below and click 'Delete'")
    delete_s_idx = st.multiselect("Select Sales Rows to Delete", filtered_sales.index.tolist())
    if st.button("Delete Selected Sales"):
        sales = sales.drop(delete_s_idx).reset_index(drop=True)
        sales.to_csv(sales_file, index=False)
        st.success("Selected sales deleted.")
        st.experimental_rerun()

# ---------- REPORTS TAB ---------- #
elif menu == "Reports":
    password = st.text_input("Enter password to view reports", type="password")
    CORRECT_PASSWORD = "gold123"  # Change as needed

    if password != CORRECT_PASSWORD:
        st.warning("Incorrect password! Reports are protected.")
        st.stop()

    st.header("Daily Profit by Product")
    if purchases.empty or sales.empty:
        st.warning("Please add purchase and sales data for report.")
    else:
        avg_purchase = purchases.groupby("Product").apply(
            lambda x: (x["Quantity"] * x["Price"]).sum() / x["Quantity"].sum() if x["Quantity"].sum() > 0 else 0
        ).to_dict()

        sales["Avg_Purchase_Price"] = sales["Product"].map(avg_purchase)
        sales["Product_Profit"] = (sales["Price"] - sales["Avg_Purchase_Price"]) * sales["Quantity"]

        daily_profit = sales.groupby(["Date", "Product"]).agg(
            Quantity_Sold=('Quantity', 'sum'),
            Sales_Revenue=('Price', lambda x: (x * sales.loc[x.index, "Quantity"]).sum()),
            Profit=('Product_Profit', 'sum')
        ).reset_index()

        # Compute stock remaining up to that date for each product
        purchases["Date"] = pd.to_datetime(purchases["Date"])
        sales["Date"] = pd.to_datetime(sales["Date"])
        daily_profit["Date"] = pd.to_datetime(daily_profit["Date"])

        stock_remaining_list = []
        for idx, row in daily_profit.iterrows():
            product = row['Product']
            date = row['Date']

            total_purchases = purchases[(purchases["Product"] == product) & (purchases["Date"] <= date)]["Quantity"].sum()
            total_sales = sales[(sales["Product"] == product) & (sales["Date"] <= date)]["Quantity"].sum()
            stock_remaining = total_purchases - total_sales
            stock_remaining_list.append(stock_remaining)

        daily_profit["Stock_Remaining"] = stock_remaining_list

        st.subheader("Profit by Date and Product (Only Sold Items)")
        st.dataframe(daily_profit.style.format({
            "Sales_Revenue": "₹{:.2f}",
            "Profit": "₹{:.2f}",
            "Quantity_Sold": "{:.0f}",
            "Stock_Remaining": "{:.0f}"
        }))

        csv = daily_profit.to_csv(index=False).encode()
        st.download_button(label="Download Daily Profit CSV", data=csv, file_name="daily_profit_report.csv", mime="text/csv")

    st.subheader("Search Any Entry (Purchase + Sales)")
    all_data = pd.concat([purchases, sales.assign(**{'Received By': ""})])
    search_term = st.text_input("Search Product or Party Name")
    date_range_all = st.date_input("Filter All Records by Date Range", [])
    filtered_all = all_data.copy()
    filtered_all = safe_filter(filtered_all, "Product", search_term)
    filtered_all = safe_filter(filtered_all, "Party Name", search_term)
    filtered_all = safe_date_filter(filtered_all, "Date", date_range_all)
    st.dataframe(filtered_all)
