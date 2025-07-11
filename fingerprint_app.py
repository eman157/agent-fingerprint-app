import streamlit as st
import pandas as pd
import os
import streamlit_authenticator as stauth

# --- Authenticator Setup ---
usernames = ['eman', 'admin']
names = ['Eman Maghraby', 'Admin User']
hashed_passwords = [
    '$2b$12$LyBEFK1UkgnL0/Nj2H4r6euK8DaEoNxi8fVasDeY1crsh9/jkG5jq'
]

authenticator = stauth.Authenticate(
    {'eman': {'name': 'Eman Maghraby', 'password': hashed_passwords[0]}},
    "agent_fingerprint_app", "abcdef", cookie_expiry_days=1
)


authenticator = stauth.Authenticate(
    dict(zip(usernames, [{"name": n, "password": p} for n, p in zip(names, hashed_passwords)])),
    "agent_fingerprint_app", "abcdef", cookie_expiry_days=1
)

name, auth_status, username = authenticator.login('Login', 'main')

# --- Main App ---
if auth_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.success(f"Welcome {name}!")

    DATA_FILE = "agents_data.xlsx"

    def load_data():
        if os.path.exists(DATA_FILE):
            return pd.read_excel(DATA_FILE, dtype=str)
        else:
            return pd.DataFrame(columns=["Name", "Agent ID", "Fingerprint ID"])

    def save_data(df):
        df.to_excel(DATA_FILE, index=False)

    def get_next_fp_id(df):
        if df.empty:
            return "1"
        else:
            # Sort by the order of insertion instead of max value
            last_fp_id = df.iloc[-1]["Fingerprint ID"]
            return str(int(last_fp_id) + 1)

    def add_agent(name, agent_id):
        df = load_data()
        if agent_id in df["Agent ID"].values:
            agent_row = df[df["Agent ID"] == agent_id].iloc[0]
            return f"Agent already exists:\n\nName: {agent_row['Name']}\nID: {agent_row['Agent ID']}\nFingerprint: {agent_row['Fingerprint ID']}"
        else:
            fp_id = get_next_fp_id(df)
            new_row = pd.DataFrame([[name, agent_id, fp_id]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            return f"Agent added successfully!\n\nName: {name}\nID: {agent_id}\nFingerprint: {fp_id}"

    def search_agent(agent_id):
        df = load_data()
        if agent_id in df["Agent ID"].values:
            agent_row = df[df["Agent ID"] == agent_id].iloc[0]
            return f"Name: {agent_row['Name']}\nID: {agent_row['Agent ID']}\nFingerprint: {agent_row['Fingerprint ID']}"
        else:
            return "Agent not found."

    # Tabs
    tab = st.sidebar.radio("Select action", ["Add Agent", "Search Agent"])

    if tab == "Add Agent":
        st.header("Add New Agent")
        name = st.text_input("Agent Name")
        agent_id = st.text_input("Agent ID")
        if st.button("Add"):
            if name and agent_id:
                msg = add_agent(name.strip(), agent_id.strip())
                st.success(msg)
            else:
                st.error("Please fill in both fields.")

    elif tab == "Search Agent":
        st.header("Search Agent by ID")
        search_id = st.text_input("Enter Agent ID")
        if st.button("Search"):
            if search_id:
                result = search_agent(search_id.strip())
                st.info(result)
            else:
                st.warning("Please enter an Agent ID.")

elif auth_status is False:
    st.error("Username or password is incorrect.")

elif auth_status is None:
    st.warning("Please enter your username and password.")
