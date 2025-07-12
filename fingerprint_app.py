import streamlit as st
import pandas as pd
import os

# --- Constants ---
DATA_FILE = "agents_data.xlsx"

st.set_page_config(page_title="Agent Fingerprint Generator", layout="centered")
st.title("🧬 Agent Fingerprint Code Generator")

# --- Load & Save ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE, dtype=str)
    else:
        return pd.DataFrame(columns=["Name", "Agent ID", "Fingerprint ID"])

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# --- Add Agent Logic ---
def add_agent(name, agent_id):
    df = load_data()

    # Check for duplicates
    if agent_id in df["Agent ID"].values:
        existing = df[df["Agent ID"] == agent_id].iloc[0]
        return {
            "status": "exists",
            "name": existing["Name"],
            "agent_id": existing["Agent ID"],
            "fingerprint_id": existing["Fingerprint ID"]
        }

    # Get last used Fingerprint ID
    if df.empty:
        last_fp_id = 1000
    else:
        last_fp_id = df["Fingerprint ID"].astype(int).max()

    new_fp_id = last_fp_id + 1
    new_row = {"Name": name, "Agent ID": agent_id, "Fingerprint ID": str(new_fp_id)}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    return {
        "status": "added",
        "name": name,
        "agent_id": agent_id,
        "fingerprint_id": str(new_fp_id)
    }

# --- Tabs ---
tab1, tab2 = st.tabs(["➕ Add Agent", "🔍 Search"])

with tab1:
    st.header("Add New Agent")
    name_input = st.text_input("Agent Name")
    id_input = st.text_input("Agent ID")

    if st.button("Generate Fingerprint Code"):
        if name_input and id_input:
            result = add_agent(name_input.strip(), id_input.strip())

            if result["status"] == "added":
                st.success("✅ Agent added successfully!")
                st.write(f"👤 Name: {result['name']}")
                st.write(f"🆔 Agent ID: {result['agent_id']}")
                st.write(f"🧬 Fingerprint ID: {result['fingerprint_id']}")
            elif result["status"] == "exists":
                st.warning("⚠️ Agent already exists!")
                st.write(f"👤 Name: {result['name']}")
                st.write(f"🆔 Agent ID: {result['agent_id']}")
                st.write(f"🧬 Fingerprint ID: {result['fingerprint_id']}")
        else:
            st.error("Please fill in both fields.")

with tab2:
    st.header("Search by Agent ID")
    search_id = st.text_input("Enter Agent ID")

    if st.button("Search"):
        df = load_data()
        if search_id in df["Agent ID"].values:
            result = df[df["Agent ID"] == search_id].iloc[0]
            st.success("✅ Agent Found")
            st.write(f"👤 Name: {result['Name']}")
            st.write(f"🆔 Agent ID: {result['Agent ID']}")
            st.write(f"🧬 Fingerprint ID: {result['Fingerprint ID']}")
        else:
            st.error("❌ Agent ID not found.")
