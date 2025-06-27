import tkinter as tk
from tkinter import ttk, messagebox

import csv
import re
import requests
from requests.auth import (HTTPBasicAuth)
import math
import random
import shutil
import os

import config
from ttkthemes import ThemedTk

from websiteConnect import *
from updateWebsite import *
from CalculateScoreRelative import *
from groupSorting import *
from ThrowersPage import *
from Credentials import *
from EventOrder import *
from UpdatePointsAndNextEvent import *

load_website_credentials()

















# score_entries = {}  # Format: { (event, full_name): entry_widget }
# total_scores = {}   # Format: { full_name: [score_per_event, ..., total] }



print("AAA")
# GUI setup
root = tk.Tk()

# root = ThemedTk(theme="adapta")  # Or "equilux", "arc", "adapta", etc.
root.title("Boomerang Tournament Manager")

# Create a Notebook widget for tabs
config.notebook = ttk.Notebook(root)
config.notebook.pack(fill="both", expand=True)

# Create throwers list tab
config.throwers_tab = ttk.Frame(config.notebook)
config.notebook.add(config.throwers_tab, text="Throwers List")

# Create Treeview for throwers display
config.tree = ttk.Treeview(config.throwers_tab, columns=("No.", "First Name", "Last Name", "Nationality", "Category"),
                    show="headings", height=10)
config.tree.heading("No.", text="No.")
config.tree.heading("First Name", text="First Name")
config.tree.heading("Last Name", text="Last Name")
config.tree.heading("Nationality", text="Nationality")
config.tree.heading("Category", text="Category")
config.tree.pack(fill="both", expand=True, padx=10, pady=10)


# Add style for restricted throwers (color code them)
# config.restricted_groups = {}  # Dictionary to keep track of restricted groups with their tags

# Load throwers from file
file_path = "input/throwers_list.txt"  # Adjust the path as needed
config.throwers = read_throwers_safe(file_path)

# Display throwers in the Treeview
display_throwers(config.tree, config.throwers)

# Load restrictions and apply colors on startup
load_restrictions()
print("restrictions: ", config.restricted_groups)

# Add UI components for adding/removing throwers
add_frame = tk.Frame(config.throwers_tab)
add_frame.pack(pady=10)

tk.Label(add_frame, text="First Name:").grid(row=0, column=0, padx=5)
config.first_name_entry = tk.Entry(add_frame)
config.first_name_entry.grid(row=0, column=1, padx=5)

tk.Label(add_frame, text="Last Name:").grid(row=1, column=0, padx=5)
config.last_name_entry = tk.Entry(add_frame)
config.last_name_entry.grid(row=1, column=1, padx=5)

tk.Label(add_frame, text="Nationality:").grid(row=2, column=0, padx=5)
config.nationality_entry = tk.Entry(add_frame)
config.nationality_entry.grid(row=2, column=1, padx=5)

tk.Label(add_frame, text="Category:").grid(row=3, column=0, padx=5)
config.category_entry = tk.Entry(add_frame)
config.category_entry.grid(row=3, column=1, padx=5)

# Buttons for add, remove, and restrict
button_frame = tk.Frame(config.throwers_tab)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Thrower", command=add_thrower)
add_button.grid(row=0, column=0, padx=10)

remove_button = tk.Button(button_frame, text="Delete Selected Thrower", command=remove_thrower)
remove_button.grid(row=0, column=1, padx=10)

restrict_button = tk.Button(button_frame, text="Restrict Couple/Group", command=restrict_couple)
restrict_button.grid(row=0, column=2, padx=10)

if config.tree is None:
    print("Tree is not initialized yet!")


remove_restriction_button = tk.Button(button_frame, text="Remove Restriction", command=remove_restriction)
remove_restriction_button.grid(row=1, column=0, padx=10)

# Bind the event to select a row for removal
config.tree.bind("<ButtonRelease-1>", lambda event: config.tree.selection())


# # === Helper: Check if two throwers are restricted ===
# def are_restricted(t1, t2):
#     name1 = f"{t1[0]} {t1[1]}"
#     name2 = f"{t2[0]} {t2[1]}"
#     for group in config.restricted_groups.values():
#         names = []
#         for item in group:
#             row_index = int(config.tree.item(item, "values")[0]) - 1
#             fn, ln, _, _ = config.throwers[row_index]
#             names.append(f"{fn} {ln}")
#         if name1 in names and name2 in names:
#             return True
#     return False


# === Website Connection Tab ===
website_tab = ttk.Frame(config.notebook)
config.notebook.add(website_tab, text="Website")

tk.Label(website_tab, text="Connect to a Website", font=("Helvetica", 14, "bold")).pack(pady=10)

form_frame = tk.Frame(website_tab)
form_frame.pack(pady=5)

tk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
config.username_entry = tk.Entry(form_frame, width=40)
config.username_entry.grid(row=0, column=1, padx=5, pady=2)

tk.Label(form_frame, text="App Password:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
config.app_password_entry = tk.Entry(form_frame, width=40, show="*")
config.app_password_entry.grid(row=1, column=1, padx=5, pady=2)

tk.Label(form_frame, text="Base URL:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
config.base_url_entry = tk.Entry(form_frame, width=40)
config.base_url_entry.grid(row=2, column=1, padx=5, pady=2)

tk.Label(form_frame, text="Tournament Slug:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
config.tournament_slug_entry = tk.Entry(form_frame, width=40)
config.tournament_slug_entry.grid(row=3, column=1, padx=5, pady=2)


button_frame = tk.Frame(website_tab)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Save Credentials", command=save_credentials_from_fields).pack(side="left", padx=10)
tk.Button(button_frame, text="Reload From File", command=load_credentials_to_fields).pack(side="left", padx=10)


# === Event Order Tab ===

# State storage
# current_event_order = []
# event_circle_counts = {}
# selected_event_index = None
# circle_entries = []

# Load from file
if os.path.exists("input/event_order.txt"):
    with open("input/event_order.txt", "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 2:
                event, circles = parts
                config.current_event_order.append(event)
                config.event_circle_counts[event] = int(circles)
            else:
                event = parts[0]
                config.current_event_order.append(event)
                config.event_circle_counts[event] = 3
else:
    config.current_event_order = [
        "Accuracy", "Fast Catch", "Endurance", "Maximum Time Aloft",
        "Trick Catch", "Aussie Round 50"
    ]
    config.event_circle_counts = {e: 3 for e in config.current_event_order}

additional_events = [
    "Accuracy", "Fast Catch", "Endurance", "Maximum Time Aloft", "Trick Catch",
    "Trick Catch 50", "Aussie Round 30", "Aussie Round 40", "Aussie Round 50",
    "Long Distance"
]

# Create tab
event_order_tab = ttk.Frame(config.notebook)
config.notebook.add(event_order_tab, text="Event Order")

config.event_frame = tk.Frame(event_order_tab)
config.event_frame.pack(pady=10)

# Header row
tk.Label(config.event_frame, text="#", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10)
tk.Label(config.event_frame, text="Event", font=("Helvetica", 12, "bold")).grid(row=0, column=1, padx=10)
tk.Label(config.event_frame, text="Circles", font=("Helvetica", 12, "bold")).grid(row=0, column=2, padx=10)



# === Add / Remove ===
add_frame = tk.Frame(event_order_tab)
add_frame.pack(pady=(5, 0))

config.event_var = tk.StringVar(value=additional_events[0])
event_dropdown = ttk.Combobox(add_frame, textvariable=config.event_var,
                              values=additional_events, state="readonly", width=25)
event_dropdown.grid(row=0, column=0, padx=5)


tk.Button(add_frame, text="Add Event", command=add_event).grid(row=0, column=1, padx=5)


tk.Button(add_frame, text="Remove Selected", command=remove_event).grid(row=0, column=2, padx=5)

# === Move / Save ===
control_frame = tk.Frame(event_order_tab)
control_frame.pack(pady=5)


tk.Button(control_frame, text="Move Up", command=move_event_up).grid(row=0, column=0, padx=10)
tk.Button(control_frame, text="Move Down", command=move_event_down).grid(row=0, column=1, padx=10)
tk.Button(control_frame, text="Save Order", command=save_event_order).grid(row=0, column=2, padx=10)

refresh_event_listboxes()


# Top-level tabs
scores_main_tab = ttk.Frame(config.notebook)
circles_main_tab = ttk.Frame(config.notebook)

config.notebook.add(scores_main_tab, text="Scores")
config.notebook.add(circles_main_tab, text="Circles")

# Sub-notebooks for event-specific tabs
config.scores_notebook = ttk.Notebook(scores_main_tab)
config.scores_notebook.pack(fill="both", expand=True)

config.circles_notebook = ttk.Notebook(circles_main_tab)
config.circles_notebook.pack(fill="both", expand=True)




config.added_score_tabs = set()  # global or module-level set





score_tab_button = tk.Button(control_frame, text="Create Score Tabs", command=create_all_score_tabs)
score_tab_button.grid(row=0, column=3, padx=10)



import webbrowser

APP_VERSION = "v1.0"

def open_website(event=None):
    webbrowser.open_new("https://www.boomerangsbynils.com")

credits_tab = ttk.Frame(config.notebook)
config.notebook.add(credits_tab, text="Credits")



tk.Label(
    credits_tab,
    text="Boomerang Tournament Manager",
    font=("Helvetica", 16, "bold")
).pack(pady=(10, 0))

tk.Label(
    credits_tab,
    text=f"Version: {APP_VERSION}",
    font=("Helvetica", 10, "italic")
).pack(pady=(0, 10))

tk.Label(
    credits_tab,
    text="Developed by:\nNils van Veen",
    font=("Helvetica", 12)
).pack()

# Clickable link
website_link = tk.Label(
    credits_tab,
    text="www.boomerangsbynils.com",
    font=("Helvetica", 12, "underline"),
    fg="blue",
    cursor="hand2"
)
website_link.pack()
website_link.bind("<Button-1>", open_website)

tk.Label(
    credits_tab,
    text="\nWith contributions from:\nManuel Schütz",
    font=("Helvetica", 12)
).pack(pady=10)

tk.Label(
    credits_tab,
    text="© 2025 Boomerang Tournament Manager\n"
         "This software is provided for personal and educational use only.\n"
         "Commercial use, redistribution, or publishing on external platforms\n"
         "without written permission is strictly prohibited.",
    font=("Helvetica", 9),
    fg="gray"
).pack(pady=(20, 10))


scoring_tab = ttk.Frame(config.notebook)
config.notebook.add(scoring_tab, text="Scoring Notes")

scoring_label = tk.Text(scoring_tab, wrap="word", font=("Helvetica", 11))
scoring_label.config(state="normal", padx=10, pady=10)





try:
    with open("input/scoring_notes.txt", "r", encoding="utf-8") as f:
        scoring_label.insert("1.0", f.read())
except FileNotFoundError:
    scoring_label.insert("1.0", "Scoring notes file not found. Please add 'scoring_notes.txt'.")

scoring_label.config(state="disabled")
scoring_label.pack(expand=True, fill="both")


root.iconbitmap("images/favicon.ico")
root.mainloop()














