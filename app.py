import streamlit as st
import json
import os
from datetime import date

# --- FILE PATHS ---
USER_DB = "users.json"
# We store tasks in a separate file or could combine them
TASK_DB = "tasks_data.json" 

# --- DATA HELPERS ---
def load_data(file):
    if not os.path.exists(file): return {}
    with open(file, "r") as f: return json.load(f)

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

# --- APP SETUP ---
st.set_page_config(page_title="Sa's Tracker", page_icon="🚀")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = ""

# --- AUTHENTICATION UI ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        u_login = st.text_input("Username")
        p_login = st.text_input("Password", type="password")
        if st.button("Log In"):
            users = load_data(USER_DB)
            if u_login in users and users[u_login] == p_login:
                st.session_state.logged_in = True
                st.session_state.user = u_login
                st.rerun()
            else:
                st.error("Invalid Username/Password")

    with tab2:
        u_reg = st.text_input("New Username")
        p_reg = st.text_input("New Password", type="password")
        if st.button("Create Account"):
            users = load_data(USER_DB)
            if u_reg in users:
                st.error("User already exists!")
            elif u_reg and p_reg:
                users[u_reg] = p_reg
                save_data(USER_DB, users)
                st.success("Registration successful! Go to Login tab.")
            else:
                st.warning("Please enter details.")

# --- MAIN TRACKER UI ---
else:
    # Sidebar for logout and adding tasks
    st.sidebar.title(f"👤 {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("✅ Daily Task Tracker")
    st.write(f"Today is: **{date.today().strftime('%A, %B %d')}**")

    # Load tasks for THIS specific user
    all_tasks = load_data(TASK_DB)
    user_tasks = all_tasks.get(st.session_state.user, [])

    # ADD TASKS SECTION
    with st.expander("➕ Add a New Task"):
        t_name = st.text_input("Task Description")
        if st.button("Add Task"):
            if t_name:
                user_tasks.append({"name": t_name, "done": False})
                all_tasks[st.session_state.user] = user_tasks
                save_data(TASK_DB, all_tasks)
                st.rerun()

    # SUCCESS CALCULATION
    total = len(user_tasks)
    done = sum(1 for t in user_tasks if t['done'])
    pct = (done / total * 100) if total > 0 else 0

    st.divider()
    
    # Progress Bar & Metric
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(pct / 100)
    with col2:
        st.metric("Success", f"{pct:.0f}%")

    # TASK LIST DISPLAY
    st.subheader("Your Tasks")
    if not user_tasks:
        st.info("No tasks yet. Add one above!")
    else:
        for i, task in enumerate(user_tasks):
            col_check, col_text, col_del = st.columns([0.1, 0.8, 0.1])
            
            # Checkbox to complete
            checked = col_check.checkbox("", value=task['done'], key=f"chk_{i}")
            if checked != task['done']:
                user_tasks[i]['done'] = checked
                all_tasks[st.session_state.user] = user_tasks
                save_data(TASK_DB, all_tasks)
                st.rerun()
            
            # Text display
            if task['done']:
                col_text.write(f"~~{task['name']}~~")
            else:
                col_text.write(task['name'])
            
            # Delete button
            if col_del.button("🗑️", key=f"del_{i}"):
                user_tasks.pop(i)
                all_tasks[st.session_state.user] = user_tasks
                save_data(TASK_DB, all_tasks)
                st.rerun()

    if st.button("Reset List for Tomorrow"):
        all_tasks[st.session_state.user] = []
        save_data(TASK_DB, all_tasks)
        st.rerun()
