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

from websiteConnect import *
from updateWebsite import *
from CalculateScoreRelative import *
from groupSorting import *
from ThrowersPage import *
from Credentials import *
from EventOrder import *
from EventOrder import add_event, remove_event

load_website_credentials()

















# score_entries = {}  # Format: { (event, full_name): entry_widget }
# total_scores = {}   # Format: { full_name: [score_per_event, ..., total] }



print("AAA")
# GUI setup
root = tk.Tk()
root.title("Boomerang Tournament Manager")

# Create a Notebook widget for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create throwers list tab
config.throwers_tab = ttk.Frame(notebook)
notebook.add(config.throwers_tab, text="Throwers List")

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
website_tab = ttk.Frame(notebook)
notebook.add(website_tab, text="Website")

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
event_order_tab = ttk.Frame(notebook)
notebook.add(event_order_tab, text="Event Order")

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
scores_main_tab = ttk.Frame(notebook)
circles_main_tab = ttk.Frame(notebook)

notebook.add(scores_main_tab, text="Scores")
notebook.add(circles_main_tab, text="Circles")

# Sub-notebooks for event-specific tabs
scores_notebook = ttk.Notebook(scores_main_tab)
scores_notebook.pack(fill="both", expand=True)

circles_notebook = ttk.Notebook(circles_main_tab)
circles_notebook.pack(fill="both", expand=True)


def update_total_points_tab():
    # Find and clear the existing Total Points tab
    for i in range(len(notebook.tabs())):
        if notebook.tab(i, "text") == "Total Points":
            notebook.forget(i)
            break

    summary_tab = ttk.Frame(notebook)
    notebook.add(summary_tab, text="Total Points")

    summary_canvas = tk.Canvas(summary_tab)
    summary_scrollbar = ttk.Scrollbar(summary_tab, orient="vertical", command=summary_canvas.yview)
    summary_frame = tk.Frame(summary_canvas)

    summary_frame.bind(
        "<Configure>",
        lambda e: summary_canvas.configure(scrollregion=summary_canvas.bbox("all"))
    )

    summary_canvas.create_window((0, 0), window=summary_frame, anchor="nw")
    summary_canvas.configure(yscrollcommand=summary_scrollbar.set)

    summary_canvas.pack(side="left", fill="both", expand=True)
    summary_scrollbar.pack(side="right", fill="y")

    # Headers
    tk.Label(summary_frame, text="Thrower Name", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    for j, event in enumerate(config.current_event_order):
        tk.Label(summary_frame, text=event, font=("Helvetica", 12, "bold")).grid(row=0, column=j + 1, padx=5, pady=5, sticky="w")
    tk.Label(summary_frame, text="Total", font=("Helvetica", 12, "bold")).grid(row=0, column=len(config.current_event_order) + 1, padx=10, pady=5, sticky="w")


    for i, thrower in enumerate(config.throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        raw_scores = config.total_scores.get(full_name, [0] * len(config.current_event_order))

        tk.Label(summary_frame, text=full_name, font=("Helvetica", 11)).grid(
            row=i + 1, column=0, sticky="w", padx=10, pady=2)

        total_points = 0
        for j, event in enumerate(config.current_event_order):
            if j < len(raw_scores):
                raw_score = raw_scores[j]
            else:
                raw_score = 0
            points = calculate_event_points(event, raw_score)
            total_points += points
            tk.Label(summary_frame, text=str(points), font=("Helvetica", 11)).grid(
                row=i + 1, column=j + 1, padx=5, pady=2)

        # FINAL total from converted scores, not raw
        tk.Label(summary_frame, text=str(total_points), font=("Helvetica", 11, "bold")).grid(
            row=i + 1, column=len(config.current_event_order) + 1, padx=10, pady=2)


def next_event_grouping():
    # Step 1: Get the current event from the selected tab
    current_tab_index = scores_notebook.index(scores_notebook.select())
    current_event = scores_notebook.tab(current_tab_index, "text")

    print("Events:", current_event, "- ", current_event);

    if current_event not in config.current_event_order:
        messagebox.showerror("Invalid Tab", "Please select a valid event tab.")
        return

    # Step 2: Save scores for current event
    save_event_results(current_event)

    # Step 3: Determine next event
    current_index = config.current_event_order.index(current_event)
    if current_index + 1 >= len(config.current_event_order):
        messagebox.showinfo("End", "No next event after this.")
        return

    next_event = config.current_event_order[current_index + 1]

    # Step 4: Build (score, thrower) list using updated total scores
    thrower_scores = []
    for thrower in config.throwers:
        full_name = f"{thrower[0]} {thrower[1]}"
        total = config.total_scores.get(full_name, [0] * (len(config.current_event_order) + 1))[-1]
        thrower_scores.append((total, thrower))

    thrower_scores.sort(reverse=True, key=lambda x: x[0])
    num_groups = config.event_circle_counts.get(next_event, 3)
    fair_groups = make_fair_competitive_groups(thrower_scores, num_groups)

    print('Debug')
    print(fair_groups) # somewhere here goes wrong with showing the groups
    # Step 5: Remove existing "[Next Event] Circles" tab if it exists
    next_tab_title = f"{next_event} Circles"
    for i in range(len(circles_notebook.tabs())):
        if circles_notebook.tab(i, "text") == next_tab_title:
            circles_notebook.forget(i)
            break

    # Step 6: Flatten and create new tab
    flat_throwers = [t for group in fair_groups for t in group]
    create_event_group_tab(next_event, flat_throwers)

    messagebox.showinfo("Circles Generated", f"Circles for '{next_event}' created based on updated scores.")






def create_event_group_tab(event_name, thrower_list):
    group_tab = ttk.Frame(circles_notebook)
    circles_notebook.add(group_tab, text=f"{event_name} Circles")

    config.tree = ttk.Treeview(group_tab, columns=("Circle", "First Name", "Last Name", "Nationality", "Category"), show="headings")
    for col in config.tree["columns"]:
        config.tree.heading(col, text=col)
    config.tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Get number of circles for this event
    num_circles = config.event_circle_counts.get(event_name, 3)
    num_circles = max(1, num_circles)

    # Distribute throwers sequentially into groups
    group_size = (len(thrower_list) + num_circles - 1) // num_circles
    groups = [thrower_list[i * group_size : (i + 1) * group_size] for i in range(num_circles)]

    for i, group in enumerate(groups, start=1):
        for thrower in group:
            config.tree.insert("", "end", values=(f"Circle {i}", *thrower))




# Modify save_accuracy_results to add the next event's score tab and group tab
def save_accuracy_results():
    event = config.current_event_order[0]
    folder = "output"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{event.lower().replace(' ', '_')}_results.csv")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Score"])

        for thrower in config.throwers:
            full_name = f"{thrower[0]} {thrower[1]}"
            entry = config.score_entries.get((event, full_name))
            if entry:
                try:
                    score = int(entry.get())
                except ValueError:
                    score = 0

                writer.writerow([full_name, score])

                if full_name not in config.total_scores:
                    config.total_scores[full_name] = [0] * len(config.current_event_order)
                event_index = config.current_event_order.index(event)
                config.total_scores[full_name][event_index] = score
                config.total_scores[full_name][-1:] = [sum(config.total_scores[full_name][:-1])]

    update_total_points_tab()
    messagebox.showinfo("Saved", f"{event} scores saved to {filename}")


# Update total_points tab to include ranking column and sorting
def update_total_points_tab():
    for i in range(len(notebook.tabs())):
        if notebook.tab(i, "text") == "Total Points":
            notebook.forget(i)
            break

    summary_tab = ttk.Frame(notebook)
    notebook.add(summary_tab, text="Total Points")

    canvas = tk.Canvas(summary_tab)
    scrollbar = ttk.Scrollbar(summary_tab, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    headers = ["Rank", "Thrower Name"] + config.current_event_order + ["Total"]
    for j, title in enumerate(headers):
        tk.Label(frame, text=title, font=("Helvetica", 12, "bold")).grid(row=0, column=j, padx=5, pady=5, sticky="w")

    scores_list = []
    for thrower in config.throwers:
        full_name = f"{thrower[0]} {thrower[1]}"
        scores = config.total_scores.get(full_name, [0] * (len(config.current_event_order) + 1))
        scores_list.append((scores[-1], full_name, scores))

    scores_list.sort(reverse=True, key=lambda x: x[0])

    for i, (_, name, scores) in enumerate(scores_list):
        tk.Label(frame, text=str(i + 1), font=("Helvetica", 11)).grid(row=i + 1, column=0, padx=5, pady=2)
        tk.Label(frame, text=name, font=("Helvetica", 11)).grid(row=i + 1, column=1, padx=5, pady=2)
        for j, s in enumerate(scores[:-1]):
            tk.Label(frame, text=str(s), font=("Helvetica", 11)).grid(row=i + 1, column=j + 2, padx=5, pady=2)
        tk.Label(frame, text=str(scores[-1]), font=("Helvetica", 11, "bold")).grid(row=i + 1, column=len(headers) - 1, padx=5, pady=2)

def save_event_results(event, summary_lines=None):
    folder = "output"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{event.lower().replace(' ', '_')}_results.csv")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Score"])

        for thrower in config.throwers:
            full_name = f"{thrower[0]} {thrower[1]}"
            entry = config.score_entries.get((event, full_name))
            if entry:
                try:
                    score = entry.get().strip()

                except ValueError:
                    score = 0

                writer.writerow([full_name, score])

                if full_name not in config.total_scores:
                    config.total_scores[full_name] = [0] * len(config.current_event_order)
                event_index = config.current_event_order.index(event)
                converted_score = calculate_event_points(event, score.strip())

                config.total_scores[full_name][event_index] = converted_score
                config.total_scores[full_name][-1:] = [sum(config.total_scores[full_name][:-1])]

    update_total_points_tab()
    messagebox.showinfo("Saved", f"{event} scores saved to {filename}")

    # Collect scores
    event_scores = {}
    for thrower in config.throwers:
        full_name = f"{thrower[0]} {thrower[1]}"
        entry = config.score_entries.get((event, full_name))
        score = entry.get().strip() if entry else "0"
        event_scores[full_name] = score

    # Generate ranked HTML
    summary_html = format_ranked_results(event, event_scores)
    update_tournament_page( event, summary_html)



def create_score_tab(event):
    if event not in config.current_event_order:
        return

    event_tab = ttk.Frame(scores_notebook)  # use the Scores sub-notebook
    scores_notebook.add(event_tab, text=event)

    canvas = tk.Canvas(event_tab)
    scrollbar = ttk.Scrollbar(event_tab, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tk.Label(scrollable_frame, text="Thrower Name", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Label(scrollable_frame, text="Score", font=("Helvetica", 12, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")

    for i, thrower in enumerate(config.throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        tk.Label(scrollable_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)
        entry = tk.Entry(scrollable_frame, width=10)
        entry.insert(0, "0")
        entry.grid(row=i + 1, column=1, padx=10, pady=2)
        config.score_entries[(event, full_name)] = entry

    button_bar = tk.Frame(scrollable_frame)
    button_bar.grid(row=len(config.throwers) + 2, column=0, columnspan=2, pady=10)

    save_btn = tk.Button(button_bar, text="Save Results", command=lambda e=event: save_event_results(e))
    save_btn.pack(side="left", padx=10)

    next_group_btn = tk.Button(button_bar, text="Next Event Grouping", command=next_event_grouping)
    next_group_btn.pack(side="left", padx=10)

    create_event_group_tab(event, config.throwers)


def create_score_tab_for_first_event_and_summary():
    if not config.current_event_order:
        messagebox.showwarning("No Events", "No events defined in the order.")
        return

    # === First Event Tab ===
    first_event = config.current_event_order[0]
    event_tab = ttk.Frame(notebook)
    notebook.add(event_tab, text=first_event)

    canvas = tk.Canvas(event_tab)
    scrollbar = ttk.Scrollbar(event_tab, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tk.Label(scrollable_frame, text="Thrower Name", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    tk.Label(scrollable_frame, text="Score", font=("Helvetica", 12, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")

    for i, thrower in enumerate(config.throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        tk.Label(scrollable_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)
        entry = tk.Entry(scrollable_frame, width=10)
        entry.insert(0, "0")
        entry.grid(row=i + 1, column=1, padx=10, pady=2)
        config.score_entries[(first_event, full_name)] = entry

    # === Final Summary Tab ===
    summary_tab = ttk.Frame(notebook)
    notebook.add(summary_tab, text="Total Points")

    summary_canvas = tk.Canvas(summary_tab)
    summary_scrollbar = ttk.Scrollbar(summary_tab, orient="vertical", command=summary_canvas.yview)
    summary_frame = tk.Frame(summary_canvas)

    summary_frame.bind(
        "<Configure>",
        lambda e: summary_canvas.configure(scrollregion=summary_canvas.bbox("all"))
    )

    summary_canvas.create_window((0, 0), window=summary_frame, anchor="nw")
    summary_canvas.configure(yscrollcommand=summary_scrollbar.set)

    summary_canvas.pack(side="left", fill="both", expand=True)
    summary_scrollbar.pack(side="right", fill="y")

    # Header Row
    tk.Label(summary_frame, text="Thrower Name", font=("Helvetica", 12, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")

    for j, event in enumerate(config.current_event_order):
        tk.Label(summary_frame, text=event, font=("Helvetica", 12, "bold")).grid(row=0, column=j + 1, padx=5, pady=5, sticky="w")

    tk.Label(summary_frame, text="Total", font=("Helvetica", 12, "bold")).grid(row=0, column=len(config.current_event_order) + 1, padx=10, pady=5, sticky="w")

    # Data Rows
    for i, thrower in enumerate(config.throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        tk.Label(summary_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)

        total_score = 0
        for j in range(len(config.current_event_order)):
            tk.Label(summary_frame, text="0", font=("Helvetica", 11)).grid(row=i + 1, column=j + 1, padx=5, pady=2)

        tk.Label(summary_frame, text=str(total_score), font=("Helvetica", 11, "bold")).grid(
            row=i + 1, column=len(config.current_event_order) + 1, padx=10, pady=2
        )

    button_bar = tk.Frame(scrollable_frame)
    button_bar.grid(row=len(config.throwers) + 2, column=0, columnspan=2, pady=10)

    save_btn = tk.Button(button_bar, text="Save Results", command=save_accuracy_results)
    save_btn.pack(side="left", padx=10)

    next_event_btn = tk.Button(button_bar, text="Next Event Grouping", command=next_event_grouping)
    next_event_btn.pack(side="left", padx=10)
    create_event_group_tab(first_event, config.throwers)


added_score_tabs = set()  # global or module-level set

def create_all_score_tabs():
    for event in config.current_event_order:
        if event not in added_score_tabs:
            create_score_tab(event)
            added_score_tabs.add(event)
            print(f"Added tab for event: {event}")
        else:
            print(f"Tab already exists for event: {event}")



score_tab_button = tk.Button(control_frame, text="Create Score Tabs", command=create_all_score_tabs)
score_tab_button.grid(row=0, column=3, padx=10)



import webbrowser

APP_VERSION = "v1.0"

def open_website(event=None):
    webbrowser.open_new("https://www.boomerangsbynils.com")

credits_tab = ttk.Frame(notebook)
notebook.add(credits_tab, text="Credits")



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


scoring_tab = ttk.Frame(notebook)
notebook.add(scoring_tab, text="Scoring Notes")

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














