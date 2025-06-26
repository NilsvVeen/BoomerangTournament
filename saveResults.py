import config
import os
import csv
from tkinter import messagebox

from CalculateScoreRelative import calculate_event_points
from Main import update_total_points_tab


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
                converted_score = calculate_event_points(event, score)
                config.total_scores[full_name][event_index] = converted_score
                config.total_scores[full_name][-1:] = [sum(config.total_scores[full_name][:-1])]

    update_total_points_tab()
    messagebox.showinfo("Saved", f"{event} scores saved to {filename}")
