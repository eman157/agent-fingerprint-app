import streamlit as st
import pandas as pd
import os

DATA_FILE = 'agents_data.xlsx'

def init_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=['Agent Name', 'Agent ID', 'Fingerprint ID'])
        df.to_excel(DATA_FILE, index=False)

def load_data():
    df = pd.read_excel(DATA_FILE, dtype=str)  # Force all columns to string
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Strip spaces
    df['Fingerprint ID'] = df['Fingerprint ID'].astype(int)  # convert FP ID back to int
    return df

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

def get_next_fingerprint_id(df):
    # Remove empty rows
    valid_rows = df.dropna(subset=['Agent Name', 'Agent ID', 'Fingerprint ID'])
    if valid_rows.empty:
        return 1
    else:
        last_fp = valid_rows.iloc[-1]['Fingerprint ID']
        return int(last_fp) + 1


def add_agent(name, agent_id):
    df = load_data()
    agent_id = agent_id.strip()
    name = name.strip()

    # Check if ID exists (after converting all to string)
    existing = df[df['Agent ID'] == agent_id]
    if not existing.empty:
        existing_row = existing.iloc[0]
        return {
            "status": "exists",
            "name": existing_row['Agent Name'],
            "id": existing_row['Agent ID'],
            "fingerprint": existing_row['Fingerprint ID']
        }

    next_fp = get_next_fingerprint_id(df)
    new_row = pd.DataFrame({
        'Agent Name': [name],
        'Agent ID': [agent_id],
        'Fingerprint ID': [next_fp]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)

    return {
        "status": "added",
        "name": name,
        "id": agent_id,
        "fingerprint": next_fp
    }

def search_agent_by_id(agent_id):
    df = load_data()
    agent_id = agent_id.strip()
    result = df[df['Agent ID'] == agent_id]
    return result

def main():
    st.set_page_config(page_title="Agent Fingerprint Generator", layout="centered")
    st.title("Agent Fingerprint Code Generator")

    tab1, tab2 = st.tabs(["➕ Add Agent", "🔍 Search Agent"])

    with tab1:
        st.subheader("Add New Agent")
        name = st.text_input("Agent Name")
        agent_id = st.text_input("Agent ID (must be unique)")

        if st.button("Add Agent"):
            if name and agent_id:
                result = add_agent(name, agent_id)
                if result["status"] == "exists":
                    st.warning("This Agent ID already exists.")
                    st.info(f"Name: {result['name']}\nID: {result['id']}\nFingerprint ID: {result['fingerprint']}")
                else:
                    st.success(f"{result['name']} was added successfully!")
                    st.success(f"Generated Fingerprint ID: {result['fingerprint']}")
            else:
                st.error("Please enter both Agent Name and Agent ID.")

    with tab2:
        st.subheader("Search Agent by ID")
        search_id = st.text_input("Enter Agent ID")

        if st.button("Search"):
            if search_id:
                result = search_agent_by_id(search_id)
                if not result.empty:
                    st.success("Agent found:")
                    st.dataframe(result)
                else:
                    st.error("No agent found with this ID.")

if __name__ == "__main__":
    init_file()
    main()
