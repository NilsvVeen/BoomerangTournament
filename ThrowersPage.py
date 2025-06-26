import config
import tkinter as tk
from tkinter import messagebox
import random
import shutil
import os

# Function to create groups based on throwers
def create_groups(throwers, group_size):
    groups = [throwers[i:i + group_size] for i in range(0, len(throwers), group_size)]
    return groups


# Function to display the throwers in a treeview
def display_throwers(tree, throwers):
    # Clear existing entries in treeview
    for item in tree.get_children():
        tree.delete(item)

    # Add numbered rows and the config.throwers data
    for i, thrower in enumerate(throwers, start=1):
        tree.insert("", "end", values=(i, *thrower))


# Function to add a thrower
def add_thrower():
    first_name = config.first_name_entry.get()
    last_name = config.last_name_entry.get()
    nationality = config.nationality_entry.get()
    category = config.category_entry.get()

    if not all([first_name, last_name, nationality, category]):
        messagebox.showerror("Input Error", "Please fill in all fields")
        return

    config.throwers.append((first_name, last_name, nationality, category))
    display_throwers(config.tree, config.throwers)
    clear_entries()
    update_throwers_file()


# Function to remove selected thrower
def remove_thrower():
    selected_item = config.tree.selection()
    if selected_item:
        confirmation = messagebox.askyesno("Delete Confirmation",
                                           "Are you sure you want to delete the selected thrower?")
        if confirmation:
            # Remove the corresponding thrower from the list using row index
            index = config.tree.index(selected_item)
            config.throwers.pop(index)
            display_throwers(config.tree, config.throwers)
            update_throwers_file()
        else:
            messagebox.showinfo("Delete Cancelled", "Deletion was cancelled.")
    else:
        messagebox.showerror("Selection Error", "Please select a thrower to remove")


# Function to restrict a couple (or group) of throwers and color code them
def restrict_couple():
    selected_items = config.tree.selection()
    if len(selected_items) < 2:
        messagebox.showerror("Selection Error", "Please select at least two throwers to restrict")
        return

    # Check if any selected thrower is already part of a restricted group
    already_restricted = [item for item in selected_items if any(item in group for group in config.restricted_groups.values())]
    if already_restricted:
        messagebox.showerror("Restriction Error",
                             f"The following throwers are already part of a restricted group: {', '.join(str(i) for i in already_restricted)}")
        return

    # Create a unique tag for each restricted group
    group_tag = f"restricted_{random.randint(1000, 9999)}"  # Generate a random tag for the group
    for item in selected_items:
        config.tree.item(item, tags=(group_tag,))

    # Add the group to the restricted groups dictionary
    config.restricted_groups[group_tag] = selected_items  # Keep track of the restricted group

    # Generate a random background color for this group
    random_color = "#{:02x}{:02x}{:02x}".format(random.randint(100, 255), random.randint(100, 255),
                                                random.randint(100, 255))

    # Set the color for this group
    set_tags(group_tag, random_color)
    update_restrictions_file()


# Function to set tags for color coding
def set_tags(group_tag, color):
    config.tree.tag_configure(group_tag, background=color, foreground="black")


# Function to clear the input fields
def clear_entries():
    config.first_name_entry.delete(0, tk.END)
    config.last_name_entry.delete(0, tk.END)
    config.nationality_entry.delete(0, tk.END)
    config.category_entry.delete(0, tk.END)


# Function to update the throwers list file (input/throwers_list.txt)
def update_throwers_file():
    with open("input/throwers_list.txt", "w", encoding="utf-8-sig") as file:
        for thrower in config.throwers:
            file.write(" | ".join(thrower) + "\n")


def update_restrictions_file():
    with open("input/restrictions.txt", "w", encoding="utf-8-sig") as file:
        for group, members in config.restricted_groups.items():
            # Loop through the selected members and match names from the throwers list
            member_names = []
            for item in members:
                # Extract the row index based on the config.treeview selection
                # Get the first column value (row number) to use as index
                row_index = int(config.tree.item(item, "values")[0]) - 1  # Adjust for zero-based indexing
                first_name, last_name, _, _ = config.throwers[row_index]
                member_names.append(f"{first_name} {last_name}")
            # Write the group of restricted throwers as a single line in the file
            file.write(f"[{', '.join(member_names)}]\n")


# Function to safely read the throwers file
def read_throwers_safe(file_path):
    config.throwers = []
    try:
        with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as file:
            for line in file:
                thrower = line.strip().split(" | ")
                if len(thrower) == 4:  # Ensure the line has the correct number of columns
                    config.throwers.append(thrower)
    except Exception as e:
        messagebox.showerror("File Read Error", f"Error reading file: {str(e)}")
    return config.throwers




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
                    for i, thrower in enumerate(config.throwers):
                        if f"{thrower[0]} {thrower[1]}" == member:
                            item_id = config.tree.get_children()[i]
                            config.tree.item(item_id, tags=(group_tag,))
                            group_items.append(item_id)
                            break

                if group_items:
                    set_tags(group_tag, random_color)
                    config.restricted_groups[group_tag] = group_items  # ✅ Add to global tracking

    except FileNotFoundError:
        print("No restrictions file found.")

    finally:
        with open("input/temp_restrictions.txt", "r", encoding="utf-8-sig") as temp_file:
            with open("input/restrictions.txt", "w", encoding="utf-8-sig") as original_file:
                original_file.write(temp_file.read())
        os.remove("input/temp_restrictions.txt")




def update_restrictions_file():
    with open("input/restrictions.txt", "w", encoding="utf-8-sig") as file:
        for group, members in config.restricted_groups.items():
            # Fetch the names of throwers from the list using their index in Treeview
            member_names = []
            for item in members:
                row_index = int(config.tree.item(item, "values")[0]) - 1  # Adjust for zero-based indexing
                first_name, last_name, _, _ = config.throwers[row_index]
                member_names.append(f"{first_name} {last_name}")
            # Write the group of restricted throwers as a single line in the file
            file.write(f"[{', '.join(member_names)}]\n")





def remove_restriction():
    selected_item = config.tree.selection()
    print(selected_item)
    if selected_item:
        selected_item = selected_item[0]  # Always unpack tuple first
        tags = config.tree.item(selected_item)["tags"]
        if not tags:
            messagebox.showinfo("No Restriction", "This thrower is not part of any restricted group.")
            return

        group_tag = tags[0]
        if group_tag in config.restricted_groups:
            del config.restricted_groups[group_tag]
            config.tree.tag_configure(group_tag, background="", foreground="")
            # Remove tag from all items in that group
            for item in config.tree.get_children():
                if group_tag in config.tree.item(item, "tags"):
                    current_tags = list(config.tree.item(item, "tags"))
                    current_tags.remove(group_tag)
                    config.tree.item(item, tags=tuple(current_tags))
            update_restrictions_file()
        else:
            messagebox.showinfo("No Restriction", "This thrower is not part of any restricted group.")
    else:
        messagebox.showerror("Selection Error", "Please select a thrower to remove the restriction.")

