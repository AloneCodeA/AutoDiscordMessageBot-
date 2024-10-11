import json
import random
import time
from datetime import datetime, timedelta
from http.client import HTTPSConnection

# User information constants
USER_ID = ""
TOKEN = ""
CHANNELS_FILE = "channels.txt"  # File containing channel info
MESSAGES_FILE = "messages.txt"  # File containing the message(s)

def get_timestamp():
    """
    Returns the current timestamp in YYYY-MM-DD HH:MM:SS format
    """
    return "[" + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "]"

def read_channels():
    """
    Reads the channels file and returns a list of channels with scheduling info.
    Each channel has a timestamp, delay, and channel ID.
    """
    try:
        with open(CHANNELS_FILE, "r", encoding="utf-8") as file:
            lines = file.read().splitlines()
            channels = []
            for i in range(0, len(lines), 4):  # Each channel info block uses 4 lines
                if lines[i].startswith("TimeStamp=") and lines[i+1].startswith("AutoDelay=") and lines[i+2].startswith("Channel="):
                    timestamp = lines[i].split("=")[1]
                    delay = int(lines[i+1].split("=")[1])
                    parts = lines[i+2].split("/")
                    if len(parts) == 6:
                        channel_url = f"https://discord.com/channels/{parts[4]}/{parts[5]}"
                        channel_id = parts[5]
                        channels.append({
                            "channel_id": channel_id,
                            "channel_url": channel_url,
                            "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") if timestamp else None,
                            "delay": delay,
                            "index": i
                        })
            return channels
    except FileNotFoundError:
        print(f"{get_timestamp()} Channels file not found.")
        return []
    except Exception as e:
        print(f"{get_timestamp()} Error reading channels file: {e}")
        return []

def update_channel_timestamp(channel):
    """
    Updates the timestamp and delay for a specific channel in the channels file.
    """
    try:
        with open(CHANNELS_FILE, "r+", encoding="utf-8") as file:
            lines = file.read().splitlines()
            index = channel['index']
            lines[index] = f"TimeStamp={channel['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if channel['timestamp'] else ''}"
            lines[index+1] = f"AutoDelay={channel['delay']}"
            lines[index+2] = f"Channel={channel['channel_url']}"
            file.seek(0)
            file.write("\n".join(lines) + "\n")
            file.truncate()
    except Exception as e:
        print(f"{get_timestamp()} Error updating channels file: {e}")

def read_messages():
    """
    Reads the messages file and returns the content as a string.
    """
    try:
        with open(MESSAGES_FILE, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"{get_timestamp()} Messages file not found.")
        return ""
    except Exception as e:
        print(f"{get_timestamp()} Error reading messages file: {e}")
        return ""

def send_message(conn, channel_id, message_data, headers):
    """
    Sends a message to a specified Discord channel using the provided connection.
    """
    try:
        conn.request("POST", f"/api/v6/channels/{channel_id}/messages", message_data, headers)
        response = conn.getresponse()
        if 199 < response.status < 300 or response.status == 429:
            print(f"{get_timestamp()} Message sent to channel {channel_id}!")
        else:
            print(f"{get_timestamp()} Failed to send message to channel {channel_id}. Status: {response.status}")
    except Exception as e:
        print(f"{get_timestamp()} Error sending message: {e} | {message_data}")

def get_connection():
    """
    Returns an HTTPS connection to Discord's API.
    """
    return HTTPSConnection("discordapp.com", 443)

def main():
    print(f"{get_timestamp()} Program started.")
    channels = read_channels()
    if not channels:
        print(f"{get_timestamp()} No channels to send messages to. Please ensure {CHANNELS_FILE} contains the correct channel information.")
        return

    headers = {
        "content-type": "application/json",
        "user-id": USER_ID,
        "authorization": TOKEN,
        "host": "discordapp.com"
    }

    while True:
        message = read_messages()
        if not message:
            print(f"{get_timestamp()} No messages to send. Please ensure {MESSAGES_FILE} contains the messages.")
            time.sleep(60)  # Wait before checking again
            continue
        
        for channel in channels:
            channel_id = channel["channel_id"]
            channel_url = channel["channel_url"]
            delay = channel["delay"]

            if not channel["timestamp"]:
                channel["timestamp"] = datetime.now()

            current_time = datetime.now()
            if current_time >= channel["timestamp"]:
                # Check if current time is between 3 AM and 10 AM
                if 3 <= current_time.hour < 10:
                    delay *= 3  # Increase delay during early hours

                headers["referrer"] = channel_url
                message_data = json.dumps({"content": message})
                conn = get_connection()
                send_message(conn, channel_id, message_data, headers)
                conn.close()

                channel["timestamp"] = current_time + timedelta(minutes=delay)
                update_channel_timestamp(channel)
                next_message_time = channel["timestamp"]
                print(f"{get_timestamp()} Next message to channel {channel_id} will be sent at {next_message_time}")
                sleep_duration = random.randint(1, 10)  # Add random delay
                time.sleep(sleep_duration)
        
        time.sleep(60)  # Wait 60 seconds before next message check

if __name__ == "__main__":
    main()
