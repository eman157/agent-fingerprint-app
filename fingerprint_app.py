import streamlit as st
import pandas as pd
import os

# File to store agent data
DATA_FILE = "agents_data.xlsx"

# Load existing data or create new
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE, dtype=str)
    else:
        return pd.DataFrame(columns=["Name", "Agent ID", "Fingerprint ID"])

# Save data to Excel
def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# Get the next fingerprint ID in sequence
def get_next_fingerprint_id(df):
    if df.empty:
        return 1
    # Get the last added row (not max value)
    last_fp_id = df["Fingerprint ID"].astype(int).iloc[-1]
    return last_fp_id + 1

# Add agent logic
def add_agent(name, agent_id):
    df = load_data()

    # Check if agent ID already exists
    existing = df[df["Agent ID"] == agent_id]
    if not existing.empty:
        return {
            "status": "exists",
            "name": existing.iloc[0]["Name"],
            "agent_id": existing.iloc[0]["Agent ID"],
            "fingerprint_id": existing.iloc[0]["Fingerprint ID"]
        }

    # Add new agent
    new_fp_id = get_next_fingerprint_id(df)
    new_row = {
        "Name": name,
        "Agent ID": agent_id,
        "Fingerprint ID": str(new_fp_id)
    }
    df.loc[len(df)] = new_row
    save_data(df)
    return {
        "status": "added",
        "Name": name,
        "Agent ID": agent_id,
        "Fingerprint ID": str(new_fp_id)
    }

# Main Streamlit app
def main():
    st.title("🔒 Agent Fingerprint Code Generator")

    tab1, tab2 = st.tabs(["➕ Add Agent", "🔍 Search Agent"])

    with tab1:
        st.header("Add New Agent")
        name_input = st.text_input("Agent Name")
        id_input = st.text_input("Agent ID")

        if st.button("Generate Fingerprint Code"):
            if name_input.strip() == "" or id_input.strip() == "":
                st.warning("Please enter both name and Agent ID.")
            else:
                result = add_agent(name_input.strip(), id_input.strip())

                if result["status"] == "exists":
                    st.warning("🚨 Agent already exists!")
                    st.markdown(f"""
                    **👤 Name:** {result['name']}  
                    **🆔 Agent ID:** {result['agent_id']}  
                    **🔒 Fingerprint ID:** {result['fingerprint_id']}
                    """)
                else:
                    st.success("✅ Agent added successfully!")
                    st.markdown(f"""
                    **👤 Name:** {result['Name']}  
                    **🆔 Agent ID:** {result['Agent ID']}  
                    **🔒 Fingerprint ID:** {result['Fingerprint ID']}
                    """)

    with tab2:
        st.header("Search Agent by ID")
        search_id = st.text_input("Enter Agent ID to search")
        if st.button("Search"):
            df = load_data()
            agent = df[df["Agent ID"] == search_id.strip()]
            if not agent.empty:
                row = agent.iloc[0]
                st.info("✅ Agent found:")
                st.markdown(f"""
                **👤 Name:** {row['Name']}  
                **🆔 Agent ID:** {row['Agent ID']}  
                **🔒 Fingerprint ID:** {row['Fingerprint ID']}
                """)
            else:
                st.error("❌ Agent not found.")

if __name__ == "__main__":
    main()
