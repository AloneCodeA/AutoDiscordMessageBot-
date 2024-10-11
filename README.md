# AutoDiscordMessageBot-
AutoDiscordMessageBot automates sending scheduled messages to multiple Discord channels. The script reads channel info and messages from external files, sends messages with adjustable delays, and handles quiet hours. Ideal for automating announcements or updates across Discord servers.

AutoDiscordMessageBot is a Python-based automation script designed to send scheduled messages to multiple Discord channels. The script reads channel information and messages from external files, schedules messages with adjustable delays, and posts them to Discord using the Discord API.

Key Features:
Reads channels and message data from files (channels.txt and messages.txt).
Sends scheduled messages to multiple Discord channels.
Supports variable delays and message scheduling with random offsets.
Automatically handles message sending even during specified quiet hours (e.g., late night).
Provides status updates and logs for each message sent.

How to Use:
Add your Discord channel information to channels.txt.
Write your message content in messages.txt.
Run the script to automate the process of sending messages at specified intervals.
