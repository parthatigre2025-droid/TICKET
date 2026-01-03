import streamlit as st
import json
import os

DATA_FILE = "train_data.json"

# ----------------- DATA HANDLING ----------------- #

DEFAULT_DATA = {
    "users": {
        "admin": {"password": "admin123", "role": "admin"},
        "user": {"password": "user123", "role": "user"}
    },
    "routes": {
        "Pune → Bhopal": {"available": 50, "booked": 0},
        "Mumbai → Delhi": {"available": 80, "booked": 0},
        "Nagpur → Hyderabad": {"available": 60, "booked": 0}
    }
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ----------------- LOGIN SYSTEM ----------------- #

def login():
    st.title("🔐 Train Booking Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        data = load_data()
        users = data["users"]

        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username]["role"]
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")


# ----------------- BOOKING LOGIC ----------------- #

def booking_dashboard():
    data = load_data()
    routes = data["routes"]

    st.title("🚆 Train Booking System")
    st.write(f"👤 Logged in as: **{st.session_state.username}** ({st.session_state.role})")

    selected_route = st.selectbox("Select Route", list(routes.keys()))
    route_data = routes[selected_route]

    col1, col2 = st.columns(2)
    col1.metric("Available Seats", route_data["available"])
    col2.metric("Booked Seats", route_data["booked"])

    st.divider()

    seats = st.number_input("Number of seats", min_value=1, step=1)

    col3, col4 = st.columns(2)

    with col3:
        if st.button("🎟️ Book Seats"):
            if seats <= route_data["available"]:
                route_data["available"] -= seats
                route_data["booked"] += seats
                save_data(data)
                st.success(f"{seats} seat(s) booked on {selected_route}")
                st.rerun()
            else:
                st.error("Not enough seats available")

    with col4:
        if st.button("❌ Cancel Seats"):
            if seats <= route_data["booked"]:
                route_data["available"] += seats
                route_data["booked"] -= seats
                save_data(data)
                st.success(f"{seats} seat(s) cancelled on {selected_route}")
                st.rerun()
            else:
                st.warning("You don't have that many seats booked")

    st.divider()

    if st.session_state.role == "admin":
        admin_panel(data)

    if st.button("Logout"):
        for key in ["logged_in", "username", "role"]:
            st.session_state.pop(key, None)
        st.rerun()


# ----------------- ADMIN PANEL ----------------- #

def admin_panel(data):
    st.subheader("🛠️ Admin Panel")

    new_route = st.text_input("Add New Route (e.g. Chennai → Kochi)")
    total_seats = st.number_input("Total Seats", min_value=1, step=1)

    if st.button("Add Route"):
        if new_route and new_route not in data["routes"]:
            data["routes"][new_route] = {
                "available": total_seats,
                "booked": 0
            }
            save_data(data)
            st.success("New route added successfully!")
            st.rerun()
        else:
            st.warning("Route already exists or invalid name")


# ----------------- APP ENTRY ----------------- #

st.set_page_config(page_title="Train Booking App", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    booking_dashboard()
