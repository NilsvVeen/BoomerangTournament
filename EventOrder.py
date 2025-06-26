
import config
import tkinter as tk
from tkinter import ttk, messagebox

# from Main import refresh_event_listboxes


def add_event():
    new_event = config.event_var.get()
    if new_event not in config.current_event_order:
        config.current_event_order.append(new_event)
        config.event_circle_counts[new_event] = 3
        refresh_event_listboxes()
    else:
        messagebox.showinfo("Duplicate", f"{new_event} is already in the list.")


def remove_event():
    # global config.selected_event_index
    if config.selected_event_index is not None:
        removed_event = config.current_event_order.pop(config.selected_event_index)
        config.event_circle_counts.pop(removed_event, None)
        config.selected_event_index = None
        refresh_event_listboxes()
    else:
        messagebox.showerror("Select Row", "Click on an event row to select it before removing.")


def move_event_up():
    # global selected_event_index
    if config.selected_event_index is None or config.selected_event_index == 0:
        return

    i = config.selected_event_index

    # Capture current circle values
    circles = []
    for entry in config.circle_entries:
        try:
            val = int(entry.get())
        except ValueError:
            val = 3
        circles.append(val)

    # Swap events and circle values
    config.current_event_order[i - 1], config.current_event_order[i] = config.current_event_order[i], config.current_event_order[i - 1]
    circles[i - 1], circles[i] = circles[i], circles[i - 1]

    # Update config.event_circle_counts
    for idx, event in enumerate(config.current_event_order):
        config.event_circle_counts[event] = circles[idx]

    config.selected_event_index -= 1
    refresh_event_listboxes()


def move_event_down():
    # global config.selected_event_index
    if config.selected_event_index is None or config.selected_event_index >= len(config.current_event_order) - 1:
        return

    i = config.selected_event_index

    # Capture current circle values
    circles = []
    for entry in config.circle_entries:
        try:
            val = int(entry.get())
        except ValueError:
            val = 3
        circles.append(val)

    # Swap events and circle values
    config.current_event_order[i], config.current_event_order[i + 1] = config.current_event_order[i + 1], config.current_event_order[i]
    circles[i], circles[i + 1] = circles[i + 1], circles[i]

    # Update config.event_circle_counts
    for idx, event in enumerate(config.current_event_order):
        config.event_circle_counts[event] = circles[idx]

    config.selected_event_index += 1
    refresh_event_listboxes()


def save_event_order():
    for i, event in enumerate(config.current_event_order):
        try:
            circles = int(config.circle_entries[i].get())
        except ValueError:
            circles = 3
        config.event_circle_counts[event] = circles

    with open("input/event_order.txt", "w", encoding="utf-8") as f:
        for event in config.current_event_order:
            f.write(f"{event}|{config.event_circle_counts[event]}\n")

    messagebox.showinfo("Saved", "Event order saved to input/event_order.txt")


def on_event_row_click(index):
    # global config.selected_event_index
    config.selected_event_index = index
    refresh_event_listboxes()

def refresh_event_listboxes():
    # global config.selected_event_index
    for widget in config.event_frame.grid_slaves():
        if int(widget.grid_info()["row"]) > 0:
            widget.destroy()
    config.circle_entries.clear()

    for idx, event in enumerate(config.current_event_order):
        # Row number
        tk.Label(config.event_frame, text=str(idx + 1), font=("Helvetica", 11)).grid(
            row=idx + 1, column=0, padx=10, pady=2, sticky="w"
        )

        # Event name (clickable)
        label = tk.Label(config.event_frame, text=event, font=("Helvetica", 11),
                         width=25, anchor="w", bg="white")
        if config.selected_event_index == idx:
            label.config(bg="#d0ebff")  # Highlight selected
        label.grid(row=idx + 1, column=1, padx=10, pady=2, sticky="w")
        label.bind("<Button-1>", lambda e, i=idx: on_event_row_click(i))

        # Circle count entry
        entry = tk.Entry(config.event_frame, width=5, font=("Helvetica", 11))
        entry.insert(0, str(config.event_circle_counts.get(event, 3)))
        entry.grid(row=idx + 1, column=2, padx=10, pady=2, sticky="w")
        config.circle_entries.append(entry)