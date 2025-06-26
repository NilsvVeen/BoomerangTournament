import config
import os


def load_website_credentials():
    try:
        with open("input/website_config.txt", "r", encoding="utf-8") as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split("=", 1)
                    print(key,value)
                    config.website_credentials[key.strip()] = value.strip()
    except FileNotFoundError:
        pass


def save_website_credentials():
    os.makedirs("input", exist_ok=True)
    with open("input/website_config.txt", "w", encoding="utf-8") as f:
        for key, value in config.website_credentials.items():
            f.write(f"{key}={value}\n")