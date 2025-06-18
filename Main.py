import tkinter as tk
from tkinter import ttk, messagebox
from readThrowers import read_throwers  # Import the function to read throwers
import random

import csv
from datetime import datetime
import os

import random

import requests
from requests.auth import HTTPBasicAuth

uploadingToWebsite = False # disabled for now avoid writing to website.


def post_to_wordpress(title, content):

    username = ''
    app_password = ''
    site_url = ''

    post_data = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = requests.post(
        site_url,
        auth=HTTPBasicAuth(username, app_password),
        json=post_data
    )

    if response.status_code == 201:
        print("✅ Posted to WordPress:", response.json()['link'])
    else:
        print("❌ Failed to post:", response.status_code, response.text)


def format_ranked_results(event_title, scores_dict):
    """
    Returns HTML <ul> with ranks.
    Do NOT return the <h2> heading — that's handled in update_tournament_page.
    """
    is_fast_catch = event_title.lower() in ["fast catch", "fc"]

    def parse_score(score):
        if isinstance(score, str):
            s = score.strip().lower()
            if s.endswith('c'):  # catches only
                try:
                    return 1000 - int(s[:-1])
                except:
                    return float('inf')
            elif '/' in s:
                try:
                    time, catches = s.replace("s", "").split("/")
                    time = float(time.strip())
                    catches = int(catches.strip().replace("c", ""))
                    return time if catches >= 5 else 1000 - catches
                except:
                    return float('inf')
            else:
                try:
                    return float(s)
                except:
                    return float('inf')
        return float(score)

    sortable = [(parse_score(score), name, score) for name, score in scores_dict.items()]
    reverse = not is_fast_catch
    sortable.sort(reverse=reverse)

    lines = ["<ul>"]
    for rank, (_, name, raw_score) in enumerate(sortable, start=1):
        lines.append(f"<li>{rank}. {name}: {raw_score}</li>")
    lines.append("</ul>")

    return "\n".join(lines)



import re
import requests
from requests.auth import HTTPBasicAuth

def update_tournament_page(tournament_slug, event_title, scores_html):
    if uploadingToWebsite: # now just disable to avoid errors

        username = ''
        app_password = ''
        base_url = ''
        auth = HTTPBasicAuth(username, app_password)

        # 1. Get page by slug
        response = requests.get(f"{base_url}?slug={tournament_slug}", auth=auth)
        if response.status_code != 200:
            print(f"❌ Failed to fetch pages: {response.status_code} {response.text}")
            return

        if response.json():
            page = response.json()[0]
            page_id = page['id']

            # 2. Fetch raw content
            detail = requests.get(f"{base_url}/{page_id}?context=edit", auth=auth)
            if detail.status_code != 200:
                print("❌ Could not fetch raw page content.")
                return

            raw_content = detail.json().get("content", {}).get("raw", "")

            # 3. Build wrapped section
            new_section = f"<!-- EVENT: {event_title} -->\n<h2>{event_title}</h2>\n{scores_html}\n<!-- END EVENT: {event_title} -->"

            # 4. Replace or insert
            pattern = rf"(?s)<!-- EVENT: {re.escape(event_title)} -->.*?<!-- END EVENT: {re.escape(event_title)} -->"
            if re.search(pattern, raw_content):
                updated_content = re.sub(pattern, new_section, raw_content)
            else:
                updated_content = raw_content.strip() + "\n\n" + new_section

            # 5. Update page
            update = requests.post(
                f"{base_url}/{page_id}",
                auth=auth,
                json={"content": updated_content}
            )

            if update.status_code == 200:
                print(f"✅ Updated event '{event_title}' in page '{tournament_slug}'.")
            else:
                print(f"❌ Failed to update page: {update.status_code} {update.text}")
        else:
            # Page doesn't exist — create it
            print(f"⚠️ Creating new page for tournament '{tournament_slug}'...")

            new_content = f"<h1>{tournament_slug.replace('-', ' ').title()}</h1>\n\n<!-- EVENT: {event_title} -->\n<h2>{event_title}</h2>\n{scores_html}\n<!-- END EVENT: {event_title} -->"
            create = requests.post(
                base_url,
                auth=auth,
                json={
                    "title": tournament_slug.replace('-', ' ').title(),
                    "slug": tournament_slug,
                    "status": "publish",
                    "content": new_content
                }
            )

            if create.status_code == 201:
                print(f"✅ Created new page '{tournament_slug}'.")
            else:
                print(f"❌ Failed to create page: {create.status_code} {create.text}")


# def make_fair_competitive_groups(throwers_with_scores, num_groups=4, block_size=5):
#     sorted_throwers = sorted(throwers_with_scores, key=lambda x: -x[0])
#     groups = [[] for _ in range(num_groups)]
#
#     # Break into blocks of N (e.g. 5-ranked groups)
#     blocks = [sorted_throwers[i:i + block_size] for i in range(0, len(sorted_throwers), block_size)]
#
#     current_index = 0
#     for block in blocks:
#         random.shuffle(block)  # small shuffle to reduce exact rank streaks
#         for thrower in block:
#             groups[current_index % num_groups].append(thrower[1])
#             current_index += 1
#
#     return groups

import math

import math

def calculate_fast_catch_points(time_taken, num_catches):
    min_time = 15
    time_limit = 60
    laps_required = 5

    # Hardcoded values for 1C–4C
    hardcoded_points = {
        1: 387,
        2: 518,
        3: 600,
        4: 659
    }

    # Convert to int for hardcoded catch lookup
    if time_taken is None:
        try:
            catches = int(num_catches)
            if catches in hardcoded_points:
                return hardcoded_points[catches]
        except:
            return 0

    try:
        num_catches = float(num_catches)
    except:
        return 0

    if num_catches >= laps_required:
        try:
            time_taken = float(time_taken)
            return math.floor(500 * math.log10(1 + 99 * min_time / time_taken))
        except:
            return 0
    else:
        try:
            ratio = (min_time / time_limit) * (num_catches / laps_required)
            return math.floor(500 * math.log10(1 + 99 * ratio))
        except:
            return 0

def calculate_event_points(event, raw_score):
    if raw_score in ["DNF", "dnf"]:
        return -100
    if raw_score in ["DNS", "np", "dns"]:
        return -200

    event = event.strip().title()

    if event in ["Fast Catch", "Fc"]:
        try:
            raw_score = str(raw_score).strip().upper()

            if raw_score.endswith("C") and "/" not in raw_score:
                catches = float(raw_score[:-1])
                return calculate_fast_catch_points(time_taken=None, num_catches=catches)

            parts = raw_score.replace("S", "").split("/")
            if len(parts) == 2:
                time_taken = float(parts[0].strip())
                num_catches = float(parts[1].strip().replace("C", ""))
                return calculate_fast_catch_points(time_taken, num_catches)

            if raw_score.replace('.', '', 1).isdigit():
                time_taken = float(raw_score)
                return calculate_fast_catch_points(time_taken, 5)

        except:
            return 0

    max_values = {
        "Accuracy": 100,
        "Aussie Round": 100,
        "Maximum Time Aloft": 50,
        "Endurance": 80,
        "Trick Catch": 100
    }

    try:
        score = float(raw_score)
        if score < 0:
            score = 0  # Clamp negative values to 0
    except:
        return 0

    max_val = max_values.get(event, 100)
    if score > max_val:
        score = max_val

    return math.floor(500 * math.log10(1 + 99 * score / max_val))





def make_fair_competitive_groups(throwers_with_scores, num_groups=4):
    sorted_throwers = sorted(throwers_with_scores, key=lambda x: -x[0])

    print("\n[DEBUG] Sorted Throwers by Score (with Ranking):")
    for rank, (score, t) in enumerate(sorted_throwers, start=1):
        print(f"  Rank {rank:2}: {t[0]} {t[1]} - Score: {score}")

    groups = [[] for _ in range(num_groups)]

    total = len(sorted_throwers)
    block_size = total // (2 * num_groups)
    print(f"\n[DEBUG] Total throwers: {total}, Num groups: {num_groups}, Block size: {block_size}")

    for g in range(num_groups):
        top_start = g * block_size
        bottom_start = total - (g + 1) * block_size

        print(f"\n[DEBUG] Group {g + 1} (Top from index {top_start}, Bottom from index {bottom_start}):")

        for i in range(block_size):
            idx = top_start + i
            if idx < total:
                thrower = sorted_throwers[idx][1]
                print(f"  Adding (Top)    Rank {idx + 1:2}: {thrower[0]} {thrower[1]}")
                groups[g].append(thrower)

        for i in range(block_size):
            idx = bottom_start + i
            if idx < total:
                thrower = sorted_throwers[idx][1]
                print(f"  Adding (Bottom) Rank {idx + 1:2}: {thrower[0]} {thrower[1]}")
                groups[g].append(thrower)

    used_indices = set()
    for g in groups:
        for p in g:
            for i, (_, name) in enumerate(sorted_throwers):
                if name == p:
                    used_indices.add(i)

    leftovers = [sorted_throwers[i][1] for i in range(total) if i not in used_indices]
    print(f"\n[DEBUG] Leftovers ({len(leftovers)}): {[f'{t[0]} {t[1]}' for t in leftovers]}")
    for i, p in enumerate(leftovers):
        group_index = i % num_groups
        print(f"  Adding leftover: {p[0]} {p[1]} to Group {group_index + 1}")
        groups[group_index].append(p)

    # === 🔄 Fix: Ensure restricted groups are in the same group using swaps ===
    print("\n[DEBUG] Fixing Restricted Groups with Swapping:")
    for tag, members in restricted_groups.items():
        # Collect all full names
        full_names = []
        for item in members:
            row_index = int(tree.item(item, "values")[0]) - 1
            first_name, last_name, *_ = throwers[row_index]
            full_names.append(f"{first_name} {last_name}")

        # Map where each restricted thrower is
        name_to_group_idx = {}
        for i, group in enumerate(groups):
            for thrower in group:
                full_name = f"{thrower[0]} {thrower[1]}"
                if full_name in full_names:
                    name_to_group_idx[full_name] = i

        unique_groups = set(name_to_group_idx.values())
        if len(unique_groups) <= 1:
            print(f"  ✅ Group already unified: {', '.join(full_names)}")
            continue

        # Choose the group with most restricted members as the target group
        from collections import Counter
        target_group = Counter(name_to_group_idx.values()).most_common(1)[0][0]
        print(f"  ⚠️  Restricted group spans multiple groups. Merging into Group {target_group + 1}")

        for full_name in full_names:
            current_group = name_to_group_idx[full_name]
            if current_group == target_group:
                continue  # already in place

            # Find the thrower object
            thrower = next(t for t in groups[current_group] if f"{t[0]} {t[1]}" == full_name)

            # Find a non-restricted person in target group to swap with
            swap_candidate = None
            for t in groups[target_group]:
                t_name = f"{t[0]} {t[1]}"
                if t_name not in full_names:
                    swap_candidate = t
                    break

            if swap_candidate:
                print(f"    🔄 Swapping {full_name} ↔ {swap_candidate[0]} {swap_candidate[1]}")
                groups[current_group].remove(thrower)
                groups[current_group].append(swap_candidate)
                groups[target_group].remove(swap_candidate)
                groups[target_group].append(thrower)
            else:
                print(f"    ❌ No swap candidate found in Group {target_group + 1}, moving {full_name} directly")
                groups[current_group].remove(thrower)
                groups[target_group].append(thrower)

    # === Final Group Print ===
    print("\n[DEBUG] Final Groups:")
    for i, group in enumerate(groups):
        group_display = []
        for t in group:
            rank = next((r + 1 for r, (_, n) in enumerate(sorted_throwers) if n == t), "?")
            group_display.append(f"{t[0]} {t[1]} (Rank {rank})")
        print(f"  Group {i + 1}: {group_display}")

    return groups




# def make_fair_competitive_groups(throwers_with_scores, num_groups=4):
#     sorted_throwers = sorted(throwers_with_scores, key=lambda x: -x[0])  # descending
#     groups = [[] for _ in range(num_groups)]
#     used_indices = set()
#
#     # Step 1: Seed top throwers (Rank 1, 2, 3, ...)
#     for group_idx in range(num_groups):
#         if group_idx < len(sorted_throwers):
#             groups[group_idx].append(sorted_throwers[group_idx][1])
#             used_indices.add(group_idx)
#
#     # Step 2: Fill with nearby competitors (±2 range from seed rank)
#     for group_idx in range(num_groups):
#         seed_idx = group_idx
#         added = 0
#         for offset in range(1, 3):  # Look at +1, +2 and -1, -2
#             for neighbor_idx in [seed_idx - offset, seed_idx + offset]:
#                 if 0 <= neighbor_idx < len(sorted_throwers) and neighbor_idx not in used_indices:
#                     groups[group_idx].append(sorted_throwers[neighbor_idx][1])
#                     used_indices.add(neighbor_idx)
#                     added += 1
#                 if added >= 2:
#                     break
#             if added >= 2:
#                 break
#
#     # Step 3: Distribute remaining throwers round-robin
#     remaining = [t[1] for i, t in enumerate(sorted_throwers) if i not in used_indices]
#     for i, thrower in enumerate(remaining):
#         groups[i % num_groups].append(thrower)
#
#     return groups

import random






def save_accuracy_results():
    event = current_event_order[0]
    folder = "output"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{event.lower().replace(' ', '_')}_results.csv")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Score"])

        for thrower in throwers:
            full_name = f"{thrower[0]} {thrower[1]}"
            entry = score_entries.get((event, full_name))
            if entry:
                try:
                    score = int(entry.get())
                except ValueError:
                    score = 0

                writer.writerow([full_name, score])

                if full_name not in total_scores:
                    total_scores[full_name] = [0] * len(current_event_order)
                event_index = current_event_order.index(event)
                converted_score = calculate_event_points(event, score)
                total_scores[full_name][event_index] = converted_score
                total_scores[full_name][-1:] = [sum(total_scores[full_name][:-1])]

    update_total_points_tab()
    messagebox.showinfo("Saved", f"{event} scores saved to {filename}")




score_entries = {}  # Format: { (event, full_name): entry_widget }
total_scores = {}   # Format: { full_name: [score_per_event, ..., total] }


# Function to create groups based on throwers
def create_groups(throwers, group_size):
    groups = [throwers[i:i + group_size] for i in range(0, len(throwers), group_size)]
    return groups


# Function to display the throwers in a treeview
def display_throwers(tree, throwers):
    # Clear existing entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Add numbered rows and the throwers data
    for i, thrower in enumerate(throwers, start=1):
        tree.insert("", "end", values=(i, *thrower))


# Function to add a thrower
def add_thrower():
    first_name = first_name_entry.get()
    last_name = last_name_entry.get()
    nationality = nationality_entry.get()
    category = category_entry.get()

    if not all([first_name, last_name, nationality, category]):
        messagebox.showerror("Input Error", "Please fill in all fields")
        return

    throwers.append((first_name, last_name, nationality, category))
    display_throwers(tree, throwers)
    clear_entries()
    update_throwers_file()


# Function to remove selected thrower
def remove_thrower():
    selected_item = tree.selection()
    if selected_item:
        confirmation = messagebox.askyesno("Delete Confirmation",
                                           "Are you sure you want to delete the selected thrower?")
        if confirmation:
            # Remove the corresponding thrower from the list using row index
            index = tree.index(selected_item)
            throwers.pop(index)
            display_throwers(tree, throwers)
            update_throwers_file()
        else:
            messagebox.showinfo("Delete Cancelled", "Deletion was cancelled.")
    else:
        messagebox.showerror("Selection Error", "Please select a thrower to remove")


# Function to restrict a couple (or group) of throwers and color code them
def restrict_couple():
    selected_items = tree.selection()
    if len(selected_items) < 2:
        messagebox.showerror("Selection Error", "Please select at least two throwers to restrict")
        return

    # Check if any selected thrower is already part of a restricted group
    already_restricted = [item for item in selected_items if any(item in group for group in restricted_groups.values())]
    if already_restricted:
        messagebox.showerror("Restriction Error",
                             f"The following throwers are already part of a restricted group: {', '.join(str(i) for i in already_restricted)}")
        return

    # Create a unique tag for each restricted group
    group_tag = f"restricted_{random.randint(1000, 9999)}"  # Generate a random tag for the group
    for item in selected_items:
        tree.item(item, tags=(group_tag,))

    # Add the group to the restricted groups dictionary
    restricted_groups[group_tag] = selected_items  # Keep track of the restricted group

    # Generate a random background color for this group
    random_color = "#{:02x}{:02x}{:02x}".format(random.randint(100, 255), random.randint(100, 255),
                                                random.randint(100, 255))

    # Set the color for this group
    set_tags(group_tag, random_color)
    update_restrictions_file()


# Function to set tags for color coding
def set_tags(group_tag, color):
    tree.tag_configure(group_tag, background=color, foreground="black")


# Function to clear the input fields
def clear_entries():
    first_name_entry.delete(0, tk.END)
    last_name_entry.delete(0, tk.END)
    nationality_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)


# Function to update the throwers list file (input/throwers_list.txt)
def update_throwers_file():
    with open("input/throwers_list.txt", "w", encoding="utf-8-sig") as file:
        for thrower in throwers:
            file.write(" | ".join(thrower) + "\n")


def update_restrictions_file():
    with open("input/restrictions.txt", "w", encoding="utf-8-sig") as file:
        for group, members in restricted_groups.items():
            # Loop through the selected members and match names from the throwers list
            member_names = []
            for item in members:
                # Extract the row index based on the Treeview selection
                # Get the first column value (row number) to use as index
                row_index = int(tree.item(item, "values")[0]) - 1  # Adjust for zero-based indexing
                first_name, last_name, _, _ = throwers[row_index]
                member_names.append(f"{first_name} {last_name}")
            # Write the group of restricted throwers as a single line in the file
            file.write(f"[{', '.join(member_names)}]\n")


# Function to safely read the throwers file
def read_throwers_safe(file_path):
    throwers = []
    try:
        with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as file:
            for line in file:
                thrower = line.strip().split(" | ")
                if len(thrower) == 4:  # Ensure the line has the correct number of columns
                    throwers.append(thrower)
    except Exception as e:
        messagebox.showerror("File Read Error", f"Error reading file: {str(e)}")
    return throwers


import shutil
import os
import random

def load_restrictions():
    try:
        shutil.copy("input/restrictions.txt", "input/temp_restrictions.txt")

        with open("input/temp_restrictions.txt", "r", encoding="utf-8-sig") as file:
            for line in file:
                members = line.strip()[1:-1].split(", ")  # Remove brackets and split names
                group_tag = f"restricted_{random.randint(1000, 9999)}"
                random_color = "#{:02x}{:02x}{:02x}".format(random.randint(100, 255), random.randint(100, 255),
                                                            random.randint(100, 255))

                group_items = []  # Store Treeview item IDs for this group

                for member in members:
                    for i, thrower in enumerate(throwers):
                        if f"{thrower[0]} {thrower[1]}" == member:
                            item_id = tree.get_children()[i]
                            tree.item(item_id, tags=(group_tag,))
                            group_items.append(item_id)
                            break

                if group_items:
                    set_tags(group_tag, random_color)
                    restricted_groups[group_tag] = group_items  # ✅ Add to global tracking

    except FileNotFoundError:
        print("No restrictions file found.")

    finally:
        with open("input/temp_restrictions.txt", "r", encoding="utf-8-sig") as temp_file:
            with open("input/restrictions.txt", "w", encoding="utf-8-sig") as original_file:
                original_file.write(temp_file.read())
        os.remove("input/temp_restrictions.txt")




def update_restrictions_file():
    with open("input/restrictions.txt", "w", encoding="utf-8-sig") as file:
        for group, members in restricted_groups.items():
            # Fetch the names of throwers from the list using their index in Treeview
            member_names = []
            for item in members:
                row_index = int(tree.item(item, "values")[0]) - 1  # Adjust for zero-based indexing
                first_name, last_name, _, _ = throwers[row_index]
                member_names.append(f"{first_name} {last_name}")
            # Write the group of restricted throwers as a single line in the file
            file.write(f"[{', '.join(member_names)}]\n")





def remove_restriction():
    selected_item = tree.selection()
    if selected_item:
        selected_item = selected_item[0]  # Always unpack tuple first
        tags = tree.item(selected_item)["tags"]
        if not tags:
            messagebox.showinfo("No Restriction", "This thrower is not part of any restricted group.")
            return

        group_tag = tags[0]
        if group_tag in restricted_groups:
            del restricted_groups[group_tag]
            tree.tag_configure(group_tag, background="", foreground="")
            # Remove tag from all items in that group
            for item in tree.get_children():
                if group_tag in tree.item(item, "tags"):
                    current_tags = list(tree.item(item, "tags"))
                    current_tags.remove(group_tag)
                    tree.item(item, tags=tuple(current_tags))
            update_restrictions_file()
        else:
            messagebox.showinfo("No Restriction", "This thrower is not part of any restricted group.")
    else:
        messagebox.showerror("Selection Error", "Please select a thrower to remove the restriction.")



# GUI setup
root = tk.Tk()
root.title("Boomerang Tournament Manager")

# Create a Notebook widget for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create throwers list tab
throwers_tab = ttk.Frame(notebook)
notebook.add(throwers_tab, text="Throwers List")

# Create Treeview for throwers display
tree = ttk.Treeview(throwers_tab, columns=("No.", "First Name", "Last Name", "Nationality", "Category"),
                    show="headings", height=10)
tree.heading("No.", text="No.")
tree.heading("First Name", text="First Name")
tree.heading("Last Name", text="Last Name")
tree.heading("Nationality", text="Nationality")
tree.heading("Category", text="Category")
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Add style for restricted throwers (color code them)
restricted_groups = {}  # Dictionary to keep track of restricted groups with their tags

# Load throwers from file
file_path = "input/throwers_list.txt"  # Adjust the path as needed
throwers = read_throwers_safe(file_path)

# Display throwers in the Treeview
display_throwers(tree, throwers)

# Load restrictions and apply colors on startup
load_restrictions()

# Add UI components for adding/removing throwers
add_frame = tk.Frame(throwers_tab)
add_frame.pack(pady=10)

tk.Label(add_frame, text="First Name:").grid(row=0, column=0, padx=5)
first_name_entry = tk.Entry(add_frame)
first_name_entry.grid(row=0, column=1, padx=5)

tk.Label(add_frame, text="Last Name:").grid(row=1, column=0, padx=5)
last_name_entry = tk.Entry(add_frame)
last_name_entry.grid(row=1, column=1, padx=5)

tk.Label(add_frame, text="Nationality:").grid(row=2, column=0, padx=5)
nationality_entry = tk.Entry(add_frame)
nationality_entry.grid(row=2, column=1, padx=5)

tk.Label(add_frame, text="Category:").grid(row=3, column=0, padx=5)
category_entry = tk.Entry(add_frame)
category_entry.grid(row=3, column=1, padx=5)

# Buttons for add, remove, and restrict
button_frame = tk.Frame(throwers_tab)
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Thrower", command=add_thrower)
add_button.grid(row=0, column=0, padx=10)

remove_button = tk.Button(button_frame, text="Delete Selected Thrower", command=remove_thrower)
remove_button.grid(row=0, column=1, padx=10)

restrict_button = tk.Button(button_frame, text="Restrict Couple/Group", command=restrict_couple)
restrict_button.grid(row=0, column=2, padx=10)

remove_restriction_button = tk.Button(button_frame, text="Remove Restriction", command=remove_restriction)
remove_restriction_button.grid(row=1, column=0, padx=10)

# Bind the event to select a row for removal
tree.bind("<ButtonRelease-1>", lambda event: tree.selection())


# === Create Groups Tab ===
groups_tab = ttk.Frame(notebook)
notebook.add(groups_tab, text="Group Generator")

group_frame = tk.Frame(groups_tab)
group_frame.pack(pady=10)

# Input: Desired group size
tk.Label(group_frame, text="Group Size:").grid(row=0, column=0, padx=5)
group_size_entry = tk.Entry(group_frame)
group_size_entry.grid(row=0, column=1, padx=5)

# Treeview to display groups
groups_tree = ttk.Treeview(groups_tab, columns=("Group", "First Name", "Last Name", "Nationality", "Category"),
                           show="headings", height=15)
for col in ("Group", "First Name", "Last Name", "Nationality", "Category"):
    groups_tree.heading(col, text=col)
groups_tree.pack(fill="both", expand=True, padx=10, pady=10)


# === Helper: Check if two throwers are restricted ===
def are_restricted(t1, t2):
    name1 = f"{t1[0]} {t1[1]}"
    name2 = f"{t2[0]} {t2[1]}"
    for group in restricted_groups.values():
        names = []
        for item in group:
            row_index = int(tree.item(item, "values")[0]) - 1
            fn, ln, _, _ = throwers[row_index]
            names.append(f"{fn} {ln}")
        if name1 in names and name2 in names:
            return True
    return False

def generate_balanced_groups():
    try:
        group_size = int(group_size_entry.get())
        if group_size <= 0:
            raise ValueError

        for item in groups_tree.get_children():
            groups_tree.delete(item)

        # Step 1: Build restricted units
        restricted_units = []
        used_indices = set()
        for group in restricted_groups.values():
            unit = []
            for item in group:
                row_index = int(tree.item(item, "values")[0]) - 1
                if row_index not in used_indices:
                    unit.append(throwers[row_index])
                    used_indices.add(row_index)
            if unit:
                restricted_units.append(unit)

        # Step 2: Group remaining throwers by category
        categories = {}
        for i, thrower in enumerate(throwers):
            if i in used_indices:
                continue
            category = thrower[3].lower()
            if category not in categories:
                categories[category] = []
            categories[category].append(thrower)

        # Step 3: Sort categories into tiers (assuming stronger throwers come first alphabetically)
        sorted_cats = sorted(categories.items(), key=lambda x: x[0])
        sorted_throwers = []
        for _, tlist in sorted_cats:
            random.shuffle(tlist)
            sorted_throwers.extend(tlist)

        # Convert single throwers to 1-element units
        unrestricted_units = [[t] for t in sorted_throwers]
        all_units = restricted_units + unrestricted_units

        # Step 4: Distribute units into groups round-robin
        num_groups = (len(throwers) + group_size - 1) // group_size
        groups = [[] for _ in range(num_groups)]

        i = 0
        for unit in all_units:
            # Find next group with enough space
            assigned = False
            for _ in range(num_groups):
                if len(groups[i]) + len(unit) <= group_size:
                    groups[i].extend(unit)
                    assigned = True
                    break
                i = (i + 1) % num_groups
            if not assigned:
                # If all groups are full, make a new one
                groups.append(unit)
            i = (i + 1) % len(groups)

        # Step 5: Display groups
        for group_num, group in enumerate(groups, start=1):
            for thrower in group:
                groups_tree.insert("", "end", values=(f"Group {group_num}", *thrower))

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid integer group size.")


def generate_groups():
    try:
        group_size = int(group_size_entry.get())
        if group_size <= 0:
            raise ValueError

        # Clear previous output
        for item in groups_tree.get_children():
            groups_tree.delete(item)

        # Step 1: Build restricted groups as units
        restricted_units = []
        used_indices = set()

        for group in restricted_groups.values():
            unit = []
            for item in group:
                row_index = int(tree.item(item, "values")[0]) - 1
                if row_index not in used_indices:
                    unit.append(throwers[row_index])
                    used_indices.add(row_index)
            if unit:
                restricted_units.append(unit)

        # Step 2: Add the remaining (non-restricted) throwers as individual units
        unrestricted_units = [
            [thrower] for i, thrower in enumerate(throwers) if i not in used_indices
        ]

        all_units = restricted_units + unrestricted_units
        random.shuffle(all_units)

        # Step 3: Form groups using units
        groups = []
        current_group = []
        for unit in all_units:
            if len(current_group) + len(unit) > group_size:
                if current_group:
                    groups.append(current_group)
                current_group = []

            current_group.extend(unit)

        if current_group:
            groups.append(current_group)

        # Step 4: Display results
        for group_num, group in enumerate(groups, start=1):
            for thrower in group:
                groups_tree.insert("", "end", values=(f"Group {group_num}", *thrower))

    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid integer group size.")


# Button to trigger group generation
generate_button = tk.Button(group_frame, text="Generate Groups", command=generate_groups)
generate_button.grid(row=0, column=2, padx=10)

balanced_button = tk.Button(group_frame, text="Generate Balanced Groups", command=generate_balanced_groups)
balanced_button.grid(row=0, column=3, padx=10)



#
#
#
# === Event Order Tab ===
event_list = ["Accuracy", "Fast Catch", "Endurance", "Maximum Time Aloft", "Trick Catch", "Aussie Round 50"]

# Dropdown options for adding events
additional_events = \
    ["Accuracy", "Fast Catch", "Endurance", "Maximum Time Aloft", "Trick Catch", "Trick Catch 50", "Aussie Round 30", "Aussie Round 40", "Aussie Round 50",
     "Long Distance"]

# Current order (copy of initial list)
current_event_order = event_list.copy()

event_order_tab = ttk.Frame(notebook)
notebook.add(event_order_tab, text="Event Order")

event_frame = tk.Frame(event_order_tab)
event_frame.pack(pady=10)

# Number listbox (left column)
event_number_listbox = tk.Listbox(event_frame, height=10, width=4, font=("Helvetica", 12), exportselection=False)
event_number_listbox.grid(row=0, column=0, rowspan=6, sticky="ns", padx=(10, 0))

# Event name listbox (right column)
event_listbox = tk.Listbox(event_frame, height=10, width=30, font=("Helvetica", 12), exportselection=False)
event_listbox.grid(row=0, column=1, rowspan=6, sticky="ns")


# === Utility ===
def refresh_event_listboxes():
    event_number_listbox.delete(0, tk.END)
    event_listbox.delete(0, tk.END)
    for idx, event in enumerate(current_event_order, start=1):
        event_number_listbox.insert(tk.END, str(idx))
        event_listbox.insert(tk.END, event)


# === Add / Remove Event ===
add_frame = tk.Frame(event_order_tab)
add_frame.pack(pady=(5, 0))

event_var = tk.StringVar(value=additional_events[0])
event_dropdown = ttk.Combobox(add_frame, textvariable=event_var, values=additional_events, state="readonly", width=25)
event_dropdown.grid(row=0, column=0, padx=5)

def add_event():
    new_event = event_var.get()
    if new_event not in current_event_order:
        current_event_order.append(new_event)
        refresh_event_listboxes()
    else:
        messagebox.showinfo("Duplicate", f"{new_event} is already in the list.")

add_event_button = tk.Button(add_frame, text="Add Event", command=add_event)
add_event_button.grid(row=0, column=1, padx=5)

def remove_event():
    selected = event_listbox.curselection()
    if selected:
        index = selected[0]
        del current_event_order[index]
        refresh_event_listboxes()
    else:
        messagebox.showerror("Selection Error", "Select an event to remove.")

remove_button = tk.Button(add_frame, text="Remove Selected Event", command=remove_event)
remove_button.grid(row=0, column=2, padx=5)


# === Move / Save ===
control_frame = tk.Frame(event_order_tab)
control_frame.pack(pady=5)

def move_event_up():
    selected = event_listbox.curselection()
    if not selected or selected[0] == 0:
        return
    i = selected[0]
    current_event_order[i], current_event_order[i - 1] = current_event_order[i - 1], current_event_order[i]
    refresh_event_listboxes()
    event_listbox.select_set(i - 1)
    event_number_listbox.select_set(i - 1)

def move_event_down():
    selected = event_listbox.curselection()
    if not selected or selected[0] == len(current_event_order) - 1:
        return
    i = selected[0]
    current_event_order[i], current_event_order[i + 1] = current_event_order[i + 1], current_event_order[i]
    refresh_event_listboxes()
    event_listbox.select_set(i + 1)
    event_number_listbox.select_set(i + 1)

def save_event_order():
    with open("input/event_order.txt", "w", encoding="utf-8") as f:
        for event in current_event_order:
            f.write(event + "\n")
    messagebox.showinfo("Saved", "Event order saved to input/event_order.txt")

up_button = tk.Button(control_frame, text="Move Up", command=move_event_up)
up_button.grid(row=0, column=0, padx=10)

down_button = tk.Button(control_frame, text="Move Down", command=move_event_down)
down_button.grid(row=0, column=1, padx=10)

save_button = tk.Button(control_frame, text="Save Order", command=save_event_order)
save_button.grid(row=0, column=2, padx=10)


# === Selection Syncing ===
def on_event_select(event):
    index = event_listbox.curselection()
    if index:
        event_number_listbox.select_clear(0, tk.END)
        event_number_listbox.select_set(index[0])

def on_number_select(event):
    index = event_number_listbox.curselection()
    if index:
        event_listbox.select_clear(0, tk.END)
        event_listbox.select_set(index[0])

event_listbox.bind("<<ListboxSelect>>", on_event_select)
event_number_listbox.bind("<<ListboxSelect>>", on_number_select)

refresh_event_listboxes()

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
    for j, event in enumerate(current_event_order):
        tk.Label(summary_frame, text=event, font=("Helvetica", 12, "bold")).grid(row=0, column=j + 1, padx=5, pady=5, sticky="w")
    tk.Label(summary_frame, text="Total", font=("Helvetica", 12, "bold")).grid(row=0, column=len(current_event_order) + 1, padx=10, pady=5, sticky="w")

    # for i, thrower in enumerate(throwers):
    #     full_name = f"{thrower[0]} {thrower[1]}"
    #     scores = total_scores.get(full_name, [0] * (len(current_event_order) + 1))
    #     tk.Label(summary_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)
    #     for j, s in enumerate(scores[:-1]):
    #         tk.Label(summary_frame, text=str(s), font=("Helvetica", 11)).grid(row=i + 1, column=j + 1, padx=5, pady=2)
    #     tk.Label(summary_frame, text=str(scores[-1]), font=("Helvetica", 11, "bold")).grid(row=i + 1, column=len(current_event_order) + 1, padx=10, pady=2)

    for i, thrower in enumerate(throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        raw_scores = total_scores.get(full_name, [0] * len(current_event_order))

        tk.Label(summary_frame, text=full_name, font=("Helvetica", 11)).grid(
            row=i + 1, column=0, sticky="w", padx=10, pady=2)

        total_points = 0
        for j, event in enumerate(current_event_order):
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
            row=i + 1, column=len(current_event_order) + 1, padx=10, pady=2)


def next_event_grouping():
    try:
        group_size = int(group_size_entry.get())
        if group_size <= 0:
            raise ValueError
    except:
        messagebox.showerror("Input Error", "Please enter a valid integer group size first.")
        return

    # Step 1: Get the current event from the selected tab
    current_tab_index = notebook.index(notebook.select())
    current_event = notebook.tab(current_tab_index, "text")

    if current_event not in current_event_order:
        messagebox.showerror("Invalid Tab", "Please select a valid event tab.")
        return

    # Step 2: Save scores for current event
    save_event_results(current_event)

    # Step 3: Determine next event
    current_index = current_event_order.index(current_event)
    if current_index + 1 >= len(current_event_order):
        messagebox.showinfo("End", "No next event after this.")
        return

    next_event = current_event_order[current_index + 1]

    # Step 4: Build (score, thrower) list using updated total scores
    thrower_scores = []
    for thrower in throwers:
        full_name = f"{thrower[0]} {thrower[1]}"
        total = total_scores.get(full_name, [0] * (len(current_event_order) + 1))[-1]
        thrower_scores.append((total, thrower))

    thrower_scores.sort(reverse=True, key=lambda x: x[0])
    num_groups = (len(throwers) + group_size - 1) // group_size
    fair_groups = make_fair_competitive_groups(thrower_scores, num_groups)

    # Step 5: Remove existing "[Next Event] Groups" tab if it exists
    next_tab_title = f"{next_event} Groups"
    for i in range(len(notebook.tabs())):
        if notebook.tab(i, "text") == next_tab_title:
            notebook.forget(i)
            break

    # Step 6: Flatten the grouped list and create the next event's group tab
    flat_throwers = [t for group in fair_groups for t in group]
    create_event_group_tab(next_event, flat_throwers)

    messagebox.showinfo("Groups Generated", f"Groups for '{next_event}' created based on updated scores.")





# Paste this helper function near your existing ones:
def create_event_group_tab(event_name, thrower_list):
    group_tab = ttk.Frame(notebook)
    notebook.add(group_tab, text=f"{event_name} Groups")

    tree = ttk.Treeview(group_tab, columns=("Group", "First Name", "Last Name", "Nationality", "Category"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    try:
        group_size = int(group_size_entry.get())
    except:
        group_size = 4  # fallback default

    groups = [thrower_list[i:i + group_size] for i in range(0, len(thrower_list), group_size)]
    for i, group in enumerate(groups, start=1):
        for thrower in group:
            tree.insert("", "end", values=(f"Group {i}", *thrower))

# Modify save_accuracy_results to add the next event's score tab and group tab
def save_accuracy_results():
    event = current_event_order[0]
    folder = "output"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{event.lower().replace(' ', '_')}_results.csv")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Score"])

        for thrower in throwers:
            full_name = f"{thrower[0]} {thrower[1]}"
            entry = score_entries.get((event, full_name))
            if entry:
                try:
                    score = int(entry.get())
                except ValueError:
                    score = 0

                writer.writerow([full_name, score])

                if full_name not in total_scores:
                    total_scores[full_name] = [0] * len(current_event_order)
                event_index = current_event_order.index(event)
                total_scores[full_name][event_index] = score
                total_scores[full_name][-1:] = [sum(total_scores[full_name][:-1])]

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

    headers = ["Rank", "Thrower Name"] + current_event_order + ["Total"]
    for j, title in enumerate(headers):
        tk.Label(frame, text=title, font=("Helvetica", 12, "bold")).grid(row=0, column=j, padx=5, pady=5, sticky="w")

    scores_list = []
    for thrower in throwers:
        full_name = f"{thrower[0]} {thrower[1]}"
        scores = total_scores.get(full_name, [0] * (len(current_event_order) + 1))
        scores_list.append((scores[-1], full_name, scores))

    scores_list.sort(reverse=True, key=lambda x: x[0])

    for i, (_, name, scores) in enumerate(scores_list):
        tk.Label(frame, text=str(i + 1), font=("Helvetica", 11)).grid(row=i + 1, column=0, padx=5, pady=2)
        tk.Label(frame, text=name, font=("Helvetica", 11)).grid(row=i + 1, column=1, padx=5, pady=2)
        for j, s in enumerate(scores[:-1]):
            tk.Label(frame, text=str(s), font=("Helvetica", 11)).grid(row=i + 1, column=j + 2, padx=5, pady=2)
        tk.Label(frame, text=str(scores[-1]), font=("Helvetica", 11, "bold")).grid(row=i + 1, column=len(headers) - 1, padx=5, pady=2)

def save_event_results(event):
    folder = "output"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{event.lower().replace(' ', '_')}_results.csv")

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Score"])

        for thrower in throwers:
            full_name = f"{thrower[0]} {thrower[1]}"
            entry = score_entries.get((event, full_name))
            if entry:
                try:
                    score = entry.get().strip()

                except ValueError:
                    score = 0

                writer.writerow([full_name, score])

                if full_name not in total_scores:
                    total_scores[full_name] = [0] * len(current_event_order)
                event_index = current_event_order.index(event)
                converted_score = calculate_event_points(event, score.strip())

                total_scores[full_name][event_index] = converted_score
                total_scores[full_name][-1:] = [sum(total_scores[full_name][:-1])]

    update_total_points_tab()
    messagebox.showinfo("Saved", f"{event} scores saved to {filename}")

    # Collect scores
    event_scores = {}
    for thrower in throwers:
        full_name = f"{thrower[0]} {thrower[1]}"
        entry = score_entries.get((event, full_name))
        score = entry.get().strip() if entry else "0"
        event_scores[full_name] = score

    # Generate ranked HTML
    summary_html = format_ranked_results(event, event_scores)
    update_tournament_page("tournament-ebc2025-results", event, summary_html)

    #
    # # Post to WordPress
    # post_to_wordpress(f"{event} Results", "\n".join(summary_lines))
    # update_tournament_page("tournament-ebc2025-results", event, "\n".join(summary_lines))


def create_score_tab(event):
    if event not in current_event_order:
        return

    event_tab = ttk.Frame(notebook)
    notebook.add(event_tab, text=event)

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

    for i, thrower in enumerate(throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        tk.Label(scrollable_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)
        entry = tk.Entry(scrollable_frame, width=10)
        entry.insert(0, "0")
        entry.grid(row=i + 1, column=1, padx=10, pady=2)
        score_entries[(event, full_name)] = entry

    # Buttons for the event tab
    button_bar = tk.Frame(scrollable_frame)
    button_bar.grid(row=len(throwers) + 2, column=0, columnspan=2, pady=10)

    save_btn = tk.Button(button_bar, text="Save Results", command=lambda e=event: save_event_results(e))
    save_btn.pack(side="left", padx=10)

    next_group_btn = tk.Button(button_bar, text="Next Event Grouping", command=next_event_grouping)
    next_group_btn.pack(side="left", padx=10)

    create_event_group_tab(event, throwers)

def create_score_tab_for_first_event_and_summary():
    if not current_event_order:
        messagebox.showwarning("No Events", "No events defined in the order.")
        return

    # === First Event Tab ===
    first_event = current_event_order[0]
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

    for i, thrower in enumerate(throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        tk.Label(scrollable_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)
        entry = tk.Entry(scrollable_frame, width=10)
        entry.insert(0, "0")
        entry.grid(row=i + 1, column=1, padx=10, pady=2)
        score_entries[(first_event, full_name)] = entry

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

    for j, event in enumerate(current_event_order):
        tk.Label(summary_frame, text=event, font=("Helvetica", 12, "bold")).grid(row=0, column=j + 1, padx=5, pady=5, sticky="w")

    tk.Label(summary_frame, text="Total", font=("Helvetica", 12, "bold")).grid(row=0, column=len(current_event_order) + 1, padx=10, pady=5, sticky="w")

    # Data Rows
    for i, thrower in enumerate(throwers):
        full_name = f"{thrower[0]} {thrower[1]}"
        tk.Label(summary_frame, text=full_name, font=("Helvetica", 11)).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)

        total_score = 0
        for j in range(len(current_event_order)):
            tk.Label(summary_frame, text="0", font=("Helvetica", 11)).grid(row=i + 1, column=j + 1, padx=5, pady=2)

        tk.Label(summary_frame, text=str(total_score), font=("Helvetica", 11, "bold")).grid(
            row=i + 1, column=len(current_event_order) + 1, padx=10, pady=2
        )

    button_bar = tk.Frame(scrollable_frame)
    button_bar.grid(row=len(throwers) + 2, column=0, columnspan=2, pady=10)

    save_btn = tk.Button(button_bar, text="Save Results", command=save_accuracy_results)
    save_btn.pack(side="left", padx=10)

    next_event_btn = tk.Button(button_bar, text="Next Event Grouping", command=next_event_grouping)
    next_event_btn.pack(side="left", padx=10)
    create_event_group_tab(first_event, throwers)


added_score_tabs = set()  # global or module-level set

def create_all_score_tabs():
    for event in current_event_order:
        if event not in added_score_tabs:
            create_score_tab(event)
            added_score_tabs.add(event)
            print(f"Added tab for event: {event}")
        else:
            print(f"Tab already exists for event: {event}")



score_tab_button = tk.Button(control_frame, text="Create Score Tabs", command=create_all_score_tabs)
score_tab_button.grid(row=0, column=3, padx=10)





root.mainloop()














