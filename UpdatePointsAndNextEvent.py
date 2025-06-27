import csv
import os

import config
import tkinter as tk
from tkinter import ttk, messagebox
from updateWebsite import *
from CalculateScoreRelative import *
from groupSorting import *


def update_total_points_tab():
    # Find and clear the existing Total Points tab
    for i in range(len(config.notebook.tabs())):
        if config.notebook.tab(i, "text") == "Total Points":
            config.notebook.forget(i)
            break

    summary_tab = ttk.Frame(config.notebook)
    config.notebook.add(summary_tab, text="Total Points")

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
    current_tab_index = config.scores_notebook.index(config.scores_notebook.select())
    current_event = config.scores_notebook.tab(current_tab_index, "text")

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
    for i in range(len(config.circles_notebook.tabs())):
        if config.circles_notebook.tab(i, "text") == next_tab_title:
            config.circles_notebook.forget(i)
            break

    # Step 6: Flatten and create new tab
    flat_throwers = [t for group in fair_groups for t in group]
    create_event_group_tab(next_event, flat_throwers)

    messagebox.showinfo("Circles Generated", f"Circles for '{next_event}' created based on updated scores.")






def create_event_group_tab(event_name, thrower_list):
    group_tab = ttk.Frame(config.circles_notebook)
    config.circles_notebook.add(group_tab, text=f"{event_name} Circles")

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
    for i in range(len(config.notebook.tabs())):
        if config.notebook.tab(i, "text") == "Total Points":
            config.notebook.forget(i)
            break

    summary_tab = ttk.Frame(config.notebook)
    config.notebook.add(summary_tab, text="Total Points")

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

    event_tab = ttk.Frame(config.scores_notebook)  # use the Scores sub-notebook
    config.scores_notebook.add(event_tab, text=event)

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
    event_tab = ttk.Frame(config.notebook)
    config.notebook.add(event_tab, text=first_event)

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
    summary_tab = ttk.Frame(config.notebook)
    config.notebook.add(summary_tab, text="Total Points")

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


def create_all_score_tabs():
    for event in config.current_event_order:
        if event not in config.added_score_tabs:
            create_score_tab(event)
            config.added_score_tabs.add(event)
            print(f"Added tab for event: {event}")
        else:
            print(f"Tab already exists for event: {event}")