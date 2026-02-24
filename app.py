import streamlit as st
import json
import os
from datetime import date
import pandas as pd

# --- CONFIG & HIGH-VISIBILITY STYLING ---
st.set_page_config(page_title="Task Tracker for Daily Life", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    /* 1. Main Background - Light & Pleasant */
    .stApp {
        background-color: #F0F4F8;
    }
    
    /* 2. FORCE DARK TEXT EVERYWHERE */
    .stApp, p, span, label, .stMarkdown {
        color: #1A202C !important;
        font-weight: 500;
    }
    
    /* 3. INPUT BOXES - WHITE Background with BLACK Text */
    input, textarea, [data-baseweb="input"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #CBD5E0 !important;
        border-radius: 8px !important;
    }
    
    /* Fix for text inside the input being visible */
    input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
    }

    /* 4. SIDEBAR - White with Dark Text */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 2px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] * {
        color: #1A202C !important;
    }

    /* 5. TABS - Higher Contrast */
    button[data-baseweb="tab"] {
        color: #4A5568 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2B6CB0 !important;
        border-bottom-color: #2B6CB0 !important;
    }

    /* 6. BUTTONS */
    .stButton>button {
        background-color: #2B6CB0;
        color: #FFFFFF !important;
        border-radius: 10px;
        font-weight: bold;
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

# --- APP LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #2B6CB0;'>Task Tracker for Daily Life</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Sign In"):
            users = load_data(USER_DB)
            if u in users and users[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else: st.error("Incorrect details.")
    with tab2:
        nu = st.text_input("New Username", key="reg_u")
        np = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Create Account"):
            users = load_data(USER_DB)
            if nu and np:
                users[nu] = np
                save_data(USER_DB, users)
                st.success("Account created!")
else:
    # --- MAIN DASHBOARD ---
    st.markdown("<h1 style='text-align: center; color: #2B6CB0;'>Task Tracker for Daily Life</h1>", unsafe_allow_html=True)
    st.write(f"Logged in as: **{st.session_state.user}** | 📅 {date.today().strftime('%A, %b %d')}")

    all_data = load_data(DATA_DB)
    user_data = all_data.get(st.session_state.user, {"daily": [], "monthly": [], "yearly": [], "history": {}})

    t1, t2, t3, t4 = st.tabs(["☀️ Daily", "📅 Monthly", "🏆 Yearly", "📊 Progress"])

    with t1:
        st.subheader("Today's Objectives")
        # High visibility input
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
            checked = col1.checkbox("", value=t['done'], key=f"d_{i}")
            if checked != t['done']:
                user_data["daily"][i]['done'] = checked
                all_data[st.session_state.user] = user_data
                save_data(DATA_DB, all_data)
                st.rerun()
            
            # Using absolute black for task names
            label = f"<span style='color: #718096; text-decoration: line-through;'>{t['name']}</span>" if t['done'] else f"<span style='color: #000000; font-weight: bold; font-size: 18px;'>{t['name']}</span>"
            col2.markdown(label, unsafe_allow_html=True)
            
            if col3.button("🗑️", key=f"del_{i}"):
                user_data["daily"].pop(i)
                all_data[st.session_state.user] = user_data
                save_data(DATA_DB, all_data)
                st.rerun()

    with t2:
        st.subheader("Monthly Milestones")
        m_in = st.text_input("New goal for this month", key="m_in_box")
        if st.button("Set Goal") and m_in:
            user_data["monthly"].append(m_in)
            save_data(DATA_DB, all_data)
            st.rerun()
        for g in user_data["monthly"]: st.info(f"📅 {g}")

    with t3:
        st.subheader("Yearly Vision")
        y_in = st.text_input("Big goal for the year", key="y_in_box")
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
