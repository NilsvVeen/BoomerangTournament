import config
import tkinter as tk
from tkinter import messagebox

def load_credentials_to_fields():

    config.username_entry.delete(0, tk.END)
    config.username_entry.insert(0, config.website_credentials["username"])
    config.app_password_entry.delete(0, tk.END)
    config.app_password_entry.insert(0, config.website_credentials["app_password"])
    config.base_url_entry.delete(0, tk.END)
    config.base_url_entry.insert(0, config.website_credentials["base_url"])
    config.tournament_slug_entry.delete(0, tk.END)
    config.tournament_slug_entry.insert(0, config.website_credentials["tournament_slug"])
    print("Credentials inserted:")
    print(config.website_credentials)

def save_credentials_from_fields():
    config.website_credentials["username"] = config.username_entry.get().strip()
    config.website_credentials["app_password"] = config.app_password_entry.get().strip()
    config.website_credentials["base_url"] = config.base_url_entry.get().strip()
    config.website_credentials["tournament_slug"] = config.tournament_slug_entry.get().strip()
    # config.website_credentials()
    messagebox.showinfo("Saved", "Website credentials saved.")
