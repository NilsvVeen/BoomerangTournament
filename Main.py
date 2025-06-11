import tkinter as tk
from tkinter import ttk, messagebox
from readThrowers import read_throwers  # Import the function to read throwers
import random


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





# Function to remove selected restriction
def remove_restriction():
    selected_item = tree.selection()
    if selected_item:
        # Get the tag of the selected item
        group_tag = tree.item(selected_item)["tags"][0]
        # Remove the restriction from restricted_groups
        print("GROUPS",  restricted_groups)
        print("tag",  group_tag)
        if group_tag in restricted_groups:
            del restricted_groups[group_tag]
            # Remove the tag and reset the color
            tree.tag_configure(group_tag, background="", foreground="")
            tree.item(selected_item, tags=())  # Clear the tag for the item
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


root.mainloop()
