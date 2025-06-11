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


# Function to remove selected thrower
def remove_thrower():
    selected_item = tree.selection()
    if selected_item:
        confirmation = messagebox.askyesno("Delete Confirmation",
                                           "Are you sure you want to delete the selected thrower?")
        if confirmation:
            # Remove the corresponding thrower from the list
            index = tree.index(selected_item)
            throwers.pop(index)
            display_throwers(tree, throwers)
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

    # Create a unique tag for each restricted group
    group_tag = f"restricted_{random.randint(1000, 9999)}"  # Generate a random tag for the group
    for item in selected_items:
        tree.item(item, tags=(group_tag,))

    restricted_groups[group_tag] = selected_items  # Keep track of the restricted group

    # Generate a random background color for this group
    random_color = "#{:02x}{:02x}{:02x}".format(random.randint(100, 255), random.randint(100, 255),
                                                random.randint(100, 255))

    # Set the color for this group
    set_tags(group_tag, random_color)


# Function to set tags for color coding
def set_tags(group_tag, color):
    tree.tag_configure(group_tag, background=color, foreground="black")


# Function to clear the input fields
def clear_entries():
    first_name_entry.delete(0, tk.END)
    last_name_entry.delete(0, tk.END)
    nationality_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)


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
throwers = read_throwers(file_path)

# Display throwers in the Treeview
display_throwers(tree, throwers)

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

# Bind the event to select a row for removal
tree.bind("<ButtonRelease-1>", lambda event: tree.selection())

root.mainloop()
