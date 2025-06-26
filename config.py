import tkinter as tk
from tkinter import ttk, messagebox


uploadingToWebsite = True # disabled for now avoid writing to website.
event_circle_counts = {}  # e.g., {"Accuracy": 3, "Fast Catch": 2}


website_credentials = {
    "username": "",
    "app_password": "",
    "base_url": "",
    "tournament_slug": ""
}

throwers = []
restricted_groups = {}  # Dictionary to keep track of restricted groups with their tags
throwers_tab = None
tree = None

# throwers page
first_name_entry = None
last_name_entry = None
nationality_entry = None
category_entry = None

score_entries = {}  # Format: { (event, full_name): entry_widget }
total_scores = {}   # Format: { full_name: [score_per_event, ..., total] }


current_event_order = []
event_circle_counts = {}
selected_event_index = None
circle_entries = []

#credentials
username_entry = None
app_password_entry = None
base_url_entry = None
tournament_slug_entry = None

event_var = None
event_frame = None