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