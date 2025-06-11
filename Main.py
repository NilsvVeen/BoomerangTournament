import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from readThrowers import read_throwers  # Import the function to read throwers


# Function to create groups based on throwers
def create_groups(throwers, group_size):
    # Simply split the throwers into groups of the given size
    groups = [throwers[i:i + group_size] for i in range(0, len(throwers), group_size)]
    return groups


# Function to display the throwers in a treeview
def display_throwers(tree, throwers):
    for thrower in throwers:
        tree.insert("", "end", values=thrower)


# Function to display the groups in the window
def display_groups(groups):
    row = 0
    for i, group in enumerate(groups):
        group_label = tk.Label(groups_frame, text=f"Group {i + 1}:")
        group_label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        row += 1

        # Display the throwers in this group
        for thrower in group:
            thrower_label = tk.Label(groups_frame, text=f"{thrower[0]} {thrower[1]} ({thrower[2]}) - {thrower[3]}")
            thrower_label.grid(row=row, column=0, sticky="w", padx=20, pady=2)
            row += 1


# GUI setup
root = tk.Tk()
root.title("Boomerang Tournament Manager")

# Create a Notebook widget for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create throwers list tab
throwers_tab = ttk.Frame(notebook)
notebook.add(throwers_tab, text="Throwers List")

# Create groups tab
groups_tab = ttk.Frame(notebook)
notebook.add(groups_tab, text="Groups")

# Create Treeview for throwers display
tree = ttk.Treeview(throwers_tab, columns=("First Name", "Last Name", "Nationality", "Category"), show="headings")
tree.heading("First Name", text="First Name")
tree.heading("Last Name", text="Last Name")
tree.heading("Nationality", text="Nationality")
tree.heading("Category", text="Category")
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Load throwers from file
file_path = "input/throwers_list.txt"  # Make sure to adjust this path if needed
throwers = read_throwers(file_path)

# Display throwers in the Treeview
display_throwers(tree, throwers)

# Create a frame for groups display
groups_frame = ttk.Frame(groups_tab)
groups_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Example usage of create_groups
group_size = 10
groups = create_groups(throwers, group_size)

# Display groups if available
if groups:
    display_groups(groups)

root.mainloop()
