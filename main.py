import streamlit as st
import pandas as pd
import json
import os

# Load user activity data
def load_user_activity():
    file_path = "user_activity.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

# Convert user activity to DataFrame
def get_activity_dataframe(activity_data):
    records = []
    for user, activities in activity_data.items():
        for entry in activities:
            records.append({
                "User": user,
                "Timestamp": entry["timestamp"],
                "Message": entry["message"],
                "Flagged Keywords": ", ".join(entry["flagged_keywords"]),
                "Suspicion Level": entry["suspicion_level"],
                "Alerted": entry["alerted"]
            })
    return pd.DataFrame(records) if records else pd.DataFrame(columns=["User", "Timestamp", "Message", "Flagged Keywords", "Suspicion Level", "Alerted"])

# Streamlit UI
st.set_page_config(page_title="User Activity Dashboard", layout="wide")
st.title("🚨 User Activity Monitoring Dashboard")

activity_data = load_user_activity()
df = get_activity_dataframe(activity_data)

# Sidebar filters
suspicion_levels = df["Suspicion Level"].unique().tolist()
selected_level = st.sidebar.multiselect("Filter by Suspicion Level", suspicion_levels, default=suspicion_levels)

filtered_df = df[df["Suspicion Level"].isin(selected_level)]
st.dataframe(filtered_df, use_container_width=True)

# Show user-specific details
selected_user = st.sidebar.selectbox("View Activity for User", ["All"] + list(activity_data.keys()))
if selected_user != "All":
    user_df = df[df["User"] == selected_user]
    st.subheader(f"Activity for {selected_user}")
    st.dataframe(user_df, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.write("📊 Live updates will reflect changes in `user_activity.json`.")
