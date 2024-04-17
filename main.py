import requests
import time
import json
import os
from colorama import init, Fore, Back

def read_statuses(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

def get_user_info(token):
    header ={
        'authorization': token
    }
    r = requests.get("https://discord.com/api/v10/users/@me", headers=header)
    if r.status_code == 200:
        user_info = r.json()
        return user_info["username"] + "#" + user_info["discriminator"], True
    else:
        return "Token invalid", False

def change_status(token, message, emoji_name, emoji_id):
    header = {
        'authorization': token
    }

    current_status = requests.get("https://discord.com/api/v8/users/@me/settings", headers=header).json()

    custom_status = current_status.get("custom_status", {})
    if custom_status is None:
        custom_status = {}
    custom_status["text"] = message
    custom_status["emoji_name"] = emoji_name
    if emoji_id:  
        custom_status["emoji_id"] = emoji_id

    jsonData = {
        "custom_status": custom_status,
        "activities": current_status.get("activities", [])
    }

    r = requests.patch("https://discord.com/api/v8/users/@me/settings", headers=header, json=jsonData)
    return r.status_code

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# ASCII art banner
banner = f"""                           ┌─                                                           ─┐
                               {Fore.MAGENTA}┬  ┬┌─┐┬  ┌─┐  {Fore.LIGHTBLACK_EX}┌─┐┌┬┐┌─┐┌┬┐┬ ┬┌─┐  ┌─┐┬ ┬┌─┐┌┐┌┌─┐┌─┐┬─┐
                               {Fore.MAGENTA}└┐┌┘├┤ │  │ │  {Fore.LIGHTBLACK_EX}└─┐ │ ├─┤ │ │ │└─┐  │  ├─┤├─┤││││ ┬├┤ ├┬┘
                               {Fore.MAGENTA} └┘ └─┘┴─┘└─┘  {Fore.LIGHTBLACK_EX}└─┘ ┴ ┴ ┴ ┴ └─┘└─┘  └─┘┴ ┴┴ ┴┘└┘└─┘└─┘┴└─
                           └─                                                           ─┘                                                                          

"""

print(banner)

config = load_config()
token = config["token"]
clear_enabled = config["clear_enabled"]
clear_interval = config["clear_interval"]
sleep_interval = config["sleep_interval"]

status_count = 0  
emoji_count = 0

while True:
    user_info, is_valid_token = get_user_info(token)
    statuses = read_statuses("text.txt")
    emojis = read_statuses("emojis.txt")
    for status in statuses:
        time_formatted = color_text(time.strftime("%I:%M %p:"), "35") 
        if is_valid_token:
            token_color_code = "32" 
        else:
            token_color_code = "31"
        token_masked = token[:10] + "*****"
        token_info = f"{token_masked} | {user_info}"
        token_colored = color_text(token_info, token_color_code)
        status_colored = color_text(status, "35") 

        emoji_data = emojis[emoji_count % len(emojis)].split(":")  
        if len(emoji_data) == 2:
            emoji_name, emoji_id = emoji_data
        elif len(emoji_data) == 1:
            emoji_name = emoji_data[0]
            emoji_id = None
        else:
            print(f"Invalid emoji: {emojis[emoji_count % len(emojis)]}")
            continue
        print(f"{time_formatted} {Fore.LIGHTBLACK_EX}Status changed for: \033[34m{token_colored}\033[90m. New status: \033[34m{status_colored}\033[0m.{Fore.LIGHTBLACK_EX} | Emoji: {emoji_name}")
        change_status(token, status, emoji_name, emoji_id)
        status_count += 1
        emoji_count += 1
        time.sleep(sleep_interval)
        if clear_enabled and status_count % clear_interval == 0:
            clear_console()
