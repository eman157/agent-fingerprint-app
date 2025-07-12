import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# إعداد الاتصال بجوجل شيت
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/11xldWqkVi3RKe9WLWzGiLskFX4vpT9VoH4HNn9eqt4s/edit#gid=0")
worksheet = sheet.get_worksheet(0)

# تحميل البيانات كـ DataFrame
def load_data():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# حفظ البيانات إلى الشيت
def save_data(df):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# توليد Fingerprint ID فريد

def generate_unique_fingerprint_id(existing_ids, last_added_id):
    current = last_added_id + 1
    while str(current) in existing_ids:
        current += 1
    return str(current)

# إضافة وكيل

def add_agent(name, agent_id):
    df = load_data()

    if agent_id in df["Agent ID"].values:
        existing = df[df["Agent ID"] == agent_id].iloc[0]
        return {
            "status": "exists",
            "name": existing["Name"],
            "agent_id": existing["Agent ID"],
            "fingerprint_id": existing["Fingerprint ID"]
        }

    used_fingerprint_ids = set(df["Fingerprint ID"].values)
    try:
        last_added_id = int(df["Fingerprint ID"].iloc[-1])
    except:
        last_added_id = 999

    new_fingerprint_id = generate_unique_fingerprint_id(used_fingerprint_ids, last_added_id)

    new_row = {
        "Name": name,
        "Agent ID": agent_id,
        "Fingerprint ID": new_fingerprint_id
    }

    df.loc[len(df)] = new_row
    save_data(df)

    return {
        "status": "added",
        "name": name,
        "agent_id": agent_id,
        "fingerprint_id": new_fingerprint_id
    }

# Streamlit UI
st.set_page_config(page_title="Agent Fingerprint ID", page_icon="\U0001F9B7")
st.title("Agent Fingerprint Code Generator")

tab1, tab2 = st.tabs(["➕ Add Agent", "🔍 Search Agent"])

with tab1:
    name = st.text_input("Agent Name")
    agent_id = st.text_input("Agent ID")

    if st.button("Add Agent"):
        if name and agent_id:
            result = add_agent(name.strip(), agent_id.strip())
            if result["status"] == "exists":
                st.warning("Agent already exists:")
            else:
                st.success("Agent added successfully!")
            st.markdown(f"""
                <div style='padding:10px;border:1px solid #ddd;border-radius:10px;background-color:#f9f9f9;'>
                <b>Status:</b> {result['status']}<br>
                <b>Name:</b> {result['name']}<br>
                <b>Agent ID:</b> {result['agent_id']}<br>
                <b>Fingerprint ID:</b> {result['fingerprint_id']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Please fill in both name and Agent ID.")

with tab2:
    search_id = st.text_input("Search by Agent ID")
    if st.button("Search"):
        df = load_data()
        result = df[df["Agent ID"] == search_id]
        if not result.empty:
            st.success("Agent found:")
            st.dataframe(result)
        else:
            st.error("Agent ID not found.")
