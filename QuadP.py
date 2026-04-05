import streamlit as st
import json
import os
import hashlib

# ==========================================
# AUTH SYSTEM
# ==========================================
USERS_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

users = load_users()

# ==========================================
# SESSION STATE INIT
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

# ==========================================
# BACKGROUND (FIXED)
# ==========================================
if not st.session_state.logged_in:
    # 🟢 LOGIN BACKGROUND
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #005E04, #0B8C10, #0ECF17, #10E63B);
    }
    </style>
    """, unsafe_allow_html=True)

else:
    # 🟣 MAIN APP BACKGROUND
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #340075, #9700FA, #B12CE8, #EFA1FF);
        overflow: hidden;
    }

    .stApp > div {
        position: relative;
        z-index: 1;
    }

    .circle {
        position: fixed;
        border-radius: 50%;
        background: radial-gradient(circle,
            rgba(177,44,232,0.8) 0%,
            rgba(151,0,250,0.6) 40%,
            rgba(52,0,117,0.3) 70%,
            transparent 100%);
        filter: blur(20px);
        animation: float 18s infinite ease-in-out;
        z-index: 0;
    }

    .circle:nth-child(1) {
        width: 300px;
        height: 300px;
        top: 5%;
        left: 10%;
    }

    .circle:nth-child(2) {
        width: 400px;
        height: 400px;
        top: 55%;
        left: 65%;
    }

    .circle:nth-child(3) {
        width: 250px;
        height: 250px;
        top: 75%;
        left: 15%;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-50px); }
        100% { transform: translateY(0px); }
    }
    </style>

    <div class="circle"></div>
    <div class="circle"></div>
    <div class="circle"></div>
    """, unsafe_allow_html=True)

# ==========================================
# LOGIN / SIGNUP PAGE
# ==========================================
if not st.session_state.logged_in:
    st.set_page_config(page_title="Pocket Planner Login", layout="centered")

    st.title("🔐 Pocket Planner Login")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # LOGIN
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")

    # SIGNUP
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if new_user in users:
                st.error("Username already exists")
            elif not new_user or not new_pass:
                st.error("Fill all fields")
            else:
                users[new_user] = hash_password(new_pass)
                save_users(users)
                st.success("Account created! You can now log in.")

    st.stop()

# ==========================================
# USER FILE
# ==========================================
username = st.session_state.get("username")
FILENAME = f"budget_{username}.json"

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(page_title="Pocket Planner", layout="centered")

# ==========================================
# LOAD / SAVE DATA
# ==========================================
def load_data():
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            return json.load(f)
    return {"limits": {}, "spent": {}, "total_budget": 0.0}

def save_data(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
category_limits = data["limits"]
category_spent = data["spent"]
total_budget_limit = data["total_budget"]

# ==========================================
# LOGOUT
# ==========================================
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.data = None
    st.rerun()

# ==========================================
# TITLE
# ==========================================
st.title(f"💰 Pocket Planner ({username})")

tab_dash, tab_manage = st.tabs(["📊 Dashboard", "⚙ Manage"])

# ==========================================
# DASHBOARD
# ==========================================
with tab_dash:
    total_allocated = sum(category_limits.values())
    total_spent_all = sum(category_spent.values())
    remaining_allocate = total_budget_limit - total_allocated

    st.info(f"Master Budget: ${total_budget_limit:.2f} | Free: ${remaining_allocate:.2f}")

    for cat in category_limits:
        limit = category_limits[cat]
        spent = category_spent.get(cat, 0)
        percent = spent / limit if limit > 0 else 0

        st.subheader(cat.upper())
        st.write(f"${spent:.2f} / ${limit:.2f}")
        st.progress(min(percent, 1.0))

        if spent > limit:
            st.error(f"⚠ OVER BY ${spent - limit:.2f}")
        else:
            st.success(f"Remaining: ${limit - spent:.2f}")

        st.divider()

    st.markdown(f"## 💵 Total Spent: ${total_spent_all:.2f}")

# ==========================================
# RESET
# ==========================================
confirm_reset = st.checkbox("I understand this will delete ALL data")

if st.button("🔄 Reset All Data"):
    if confirm_reset:
        st.session_state.data = {"limits": {}, "spent": {}, "total_budget": 0.0}
        save_data(st.session_state.data)
        st.rerun()
    else:
        st.error("Please confirm before resetting.")

# ==========================================
# MANAGE
# ==========================================
with tab_manage:

    st.subheader("1️⃣ Set Total Monthly Budget")
    new_budget = st.number_input("Total Budget", min_value=0.0, value=float(total_budget_limit))

    if st.button("SET BUDGET"):
        if new_budget >= sum(category_limits.values()):
            data["total_budget"] = new_budget
            save_data(data)
            st.rerun()
        else:
            st.error("Budget too small")

    st.divider()

    st.subheader("2️⃣ Create Category")
    cat_name = st.text_input("Category Name")
    cat_limit = st.number_input("Category Limit", min_value=0.0)

    if st.button("CREATE CATEGORY"):
        if cat_name:
            if sum(category_limits.values()) + cat_limit <= total_budget_limit:
                category_limits[cat_name] = cat_limit
                category_spent[cat_name] = 0.0
                save_data(data)
                st.rerun()
            else:
                st.error("Not enough budget")

    st.divider()

    st.subheader("3️⃣ Add Expense")

    if category_limits:
        exp_cat = st.selectbox("Category", list(category_limits.keys()))
        exp_amt = st.slider("Amount", 0.0, 1000.0)

        if st.button("ADD EXPENSE"):
            category_spent[exp_cat] += exp_amt
            save_data(data)
            st.rerun()
    else:
        st.warning("Create a category first")