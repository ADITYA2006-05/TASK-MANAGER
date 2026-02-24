import streamlit as st
import json
import os
from datetime import date
import pandas as pd

# --- CONFIG & READABLE UI STYLING ---
st.set_page_config(page_title="Task Tracker for Daily Life", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    /* Calming Light Background */
    .stApp {
        background-color: #F0F4F8;
    }
    
    /* Main Text - Dark Charcoal for visibility */
    .stApp, p, span, label {
        color: #1A202C !important;
        font-weight: 500;
    }
    
    /* Headers - Deep Blue/Black */
    h1, h2, h3 {
        color: #2D3748 !important;
        font-weight: 700 !important;
    }

    /* Soft Cards for Tasks */
    .stCheckbox {
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #CBD5E0;
        margin-bottom: 5px;
    }

    /* Primary Action Buttons */
    .stButton>button {
        background-color: #2B6CB0;
        color: #FFFFFF !important;
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* Success Metric - Bold Dark Green */
    [data-testid="stMetricValue"] {
        color: #22543D !important;
        font-weight: 800;
    }

    /* Input Fields */
    input {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA HELPERS ---
USER_DB = "users.json"
DATA_DB = "planner_data.json"

def load_data(file):
    if not os.path.exists(file): return {}
    with open(file, "r") as f: return json.load(f)

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- AUTH UI ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>Task Tracker for Daily Life</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Sign In"):
            users = load_data(USER_DB)
            if u in users and users[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Incorrect details.")
    with tab2:
        nu, np = st.text_input("New Username"), st.text_input("New Password", type="password")
        if st.button("Create Account"):
            users = load_data(USER_DB)
            if nu and np:
                users[nu] = np
                save_data(USER_DB, users)
                st.success("Account created!")

# --- MAIN APP UI ---
else:
    st.markdown("<h1 style='text-align: center;'>Task Tracker for Daily Life</h1>", unsafe_allow_html=True)
    st.write(f"Logged in as: **{st.session_state.user}** | 📅 {date.today().strftime('%A, %b %d')}")

    all_data = load_data(DATA_DB)
    user_data = all_data.get(st.session_state.user, {"daily": [], "monthly": [], "yearly": [], "history": {}})

    t1, t2, t3, t4 = st.tabs(["☀️ Daily", "📅 Monthly", "🏆 Yearly", "📊 Progress"])

    with t1:
        st.subheader("Today's Objectives")
        new_task = st.text_input("What is your top priority today?", key="d_in")
        if st.button("Add Task") and new_task:
            user_data["daily"].append({"name": new_task, "done": False})
            all_data[st.session_state.user] = user_data
            save_data(DATA_DB, all_data)
            st.rerun()

        done = sum(1 for t in user_data["daily"] if t['done'])
        total = len(user_data["daily"])
        pct = (done/total*100) if total > 0 else 0
        
        c1, c2 = st.columns(2)
        c1.metric("Completed", f"{done}/{total}")
        c2.metric("Success Rate", f"{pct:.0f}%")
        st.progress(pct/100)

        st.divider()
        for i, t in enumerate(user_data["daily"]):
            col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
            if col1.checkbox("", value=t['done'], key=f"d_{i}"):
                user_data["daily"][i]['done'] = True
            else: user_data["daily"][i]['done'] = False
            
            # Use Dark Grey for normal, Gray for strikethrough
            label = f"<span style='color: #718096; text-decoration: line-through;'>{t['name']}</span>" if t['done'] else f"<span style='color: #000000; font-weight: bold;'>{t['name']}</span>"
            col2.markdown(label, unsafe_allow_html=True)
            
            if col3.button("🗑️", key=f"del_{i}"):
                user_data["daily"].pop(i)
                all_data[st.session_state.user] = user_data
                save_data(DATA_DB, all_data)
                st.rerun()
        
        # Save historical progress
        user_data["history"][str(date.today())] = pct
        all_data[st.session_state.user] = user_data
        save_data(DATA_DB, all_data)

    with t2:
        st.subheader("Monthly Milestones")
        m_in = st.text_input("New goal for this month")
        if st.button("Set Goal") and m_in:
            user_data["monthly"].append(m_in)
            save_data(DATA_DB, all_data)
            st.rerun()
        for g in user_data["monthly"]: st.info(f"📅 {g}")

    with t3:
        st.subheader("Yearly Vision")
        y_in = st.text_input("Big goal for the year")
        if st.button("Set Vision") and y_in:
            user_data["yearly"].append(y_in)
            save_data(DATA_DB, all_data)
            st.rerun()
        for g in user_data["yearly"]: st.warning(f"🏆 {g}")

    with t4:
        st.subheader("Performance History")
        if user_data["history"]:
            df = pd.DataFrame(list(user_data["history"].items()), columns=['Date', 'Success%'])
            st.line_chart(df.set_index('Date'))

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
