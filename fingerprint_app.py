import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import os

# ========== CONFIG ==========
DATA_FILE = "agents_data.xlsx"

# ✅ كلمة مرور مشفرة جاهزة لـ Naosfp@2025
credentials = {
    "usernames": {
        "eman": {
            "name": "Eman Maghraby",
            "password": "$2b$12$9H0XnToTLfYP9aPAwqt5pO0pUv0c0KDYK7hO3NSkEpIEwR3K5Ioe2"
        }
    }
}

# ========== AUTHENTICATION ==========
authenticator = stauth.Authenticate(
    credentials,
    "agent_fingerprint_app",
    "abcdef",  # مفتاح الكوكيز
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", location="main")

# دالة لاستخراج الرقم فقط من Fingerprint ID
def extract_fp_number(fp_id):
    return ''.join(filter(str.isdigit, fp_id)) if fp_id else ""

if authentication_status:
    authenticator.logout("Logout", location="sidebar")
    st.sidebar.success(f"Welcome {name}!")

    st.title("🔐 Agent Fingerprint Code Generator")

    # ========== Functions ==========
    def load_data():
        if os.path.exists(DATA_FILE):
            return pd.read_excel(DATA_FILE, dtype=str)
        else:
            return pd.DataFrame(columns=["Agent Name", "Agent ID", "Fingerprint ID"])

    def save_data(df):
        df.to_excel(DATA_FILE, index=False)

    def get_next_fp_code(df):
        if df.empty:
            return "FP0001"
        else:
            existing_codes = df["Fingerprint ID"].astype(str).str.extract(r'(\d+)')[0].astype(int)
            last_index = df.index[-1]
            return f"FP{existing_codes[last_index] + 1:04d}"

    def add_agent(name, agent_id):
        df = load_data()
        if agent_id in df['Agent ID'].values:
            existing = df[df['Agent ID'] == agent_id].iloc[0]
            return f"Agent already exists!", existing['Agent Name'], existing['Agent ID'], existing['Fingerprint ID']
        else:
            fp_code = get_next_fp_code(df)
            df.loc[len(df)] = [name, agent_id, fp_code]
            save_data(df)
            return "Agent added successfully!", name, agent_id, fp_code

    def search_agent(agent_id):
        df = load_data()
        match = df[df['Agent ID'] == agent_id]
        if not match.empty:
            row = match.iloc[0]
            return True, row['Agent Name'], row['Agent ID'], row['Fingerprint ID']
        else:
            return False, None, None, None

    # ========== Tabs ==========
    tab1, tab2 = st.tabs(["➕ Add Agent", "🔍 Search Agent"])

    with tab1:
        st.header("➕ Add New Agent")
        name_input = st.text_input("Agent Name")
        id_input = st.text_input("Agent ID")

        if st.button("Create Fingerprint Code"):
            if name_input and id_input:
                msg, name, aid, fpid = add_agent(name_input.strip(), id_input.strip())
                st.success(msg)
                st.write(f"**Name:** {name}")
                st.write(f"**Agent ID:** {aid}")
                st.write(f"**Fingerprint ID:** {extract_fp_number(fpid)}")
            else:
                st.warning("Please fill in all fields.")

    with tab2:
        st.header("🔍 Search by Agent ID")
        search_id = st.text_input("Enter Agent ID to search")

        if st.button("Search"):
            found, name, aid, fpid = search_agent(search_id.strip())
            if found:
                st.success("Agent found:")
                st.write(f"**Name:** {name}")
                st.write(f"**Agent ID:** {aid}")
                st.write(f"**Fingerprint ID:** {extract_fp_number(fpid)}")
            else:
                st.error("Agent not found.")

else:
    st.error("Please log in to continue.")
