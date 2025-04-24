import os
from telethon import TelegramClient
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime
import re
from dotenv import load_dotenv
from collections import defaultdict

# Load .env file
load_dotenv()

# Get information from .env file for both accounts
api_id_1 = os.getenv('API_ID_1')
api_hash_1 = os.getenv('API_HASH_1')
phone_1 = os.getenv('PHONE_1')

api_id_2 = os.getenv('API_ID_2')
api_hash_2 = os.getenv('API_HASH_2')
phone_2 = os.getenv('PHONE_2')

# Get optional default sender mappings from .env file
default_from_name_1 = os.getenv('DEFAULT_FROM_NAME_1')
default_from_name_2 = os.getenv('DEFAULT_FROM_NAME_2')

# Get group chat name from .env file
group_chat_name = os.getenv('GROUP_CHAT_NAME')

# Path to export folder
export_folder = os.path.dirname(__file__)

client1 = TelegramClient('session_user1', api_id_1, api_hash_1)
client2 = TelegramClient('session_user2', api_id_2, api_hash_2)


async def process_time_format(message_time_raw):
    if not message_time_raw:
        return "Unknown time"
    try:
        pattern = r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2}):(\d{2})\s+UTC([+-]\d{2}):(\d{2})'
        match = re.match(pattern, message_time_raw)
        if match:
            day, month, year, hour, minute, second, tz_hour, tz_minute = match.groups()
            return f"{day}/{month}/{year} - {hour}:{minute}:{second}"
        return "Unknown time"
    except Exception as e:
        print(f"Time processing error: {message_time_raw}, error: {e}")
        return "Unknown time"


def detect_senders_from_html(html_files):
    """Auto-detect sender names from HTML files and count their frequency"""
    sender_counts = defaultdict(int)

    for html_file in html_files:
        file_path = os.path.join(export_folder, html_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        from_name_tags = soup.find_all('div', class_='from_name')
        for tag in from_name_tags:
            name = tag.get_text(strip=True)
            if name:  # Ignore empty names
                sender_counts[name] += 1

    # Sort senders by frequency, most frequent first
    sorted_senders = sorted(sender_counts.items(),
                            key=lambda x: x[1], reverse=True)

    # Return the list of sender names
    return [name for name, count in sorted_senders]


async def main():
    if not all([api_id_1, api_hash_1, phone_1, api_id_2, api_hash_2, phone_2, group_chat_name]):
        print("Missing account information in .env file")
        return

    await client1.start(phone_1)
    await client2.start(phone_2)

    group_entity = await client1.get_input_entity(group_chat_name)
    group_entity2 = await client2.get_input_entity(group_chat_name)

    html_files = sorted([f for f in os.listdir(export_folder)
                         if f.startswith('messages') and f.endswith('.html')])

    if not html_files:
        print("No HTML files found in the directory")
        return

    # Detect senders from HTML files
    senders = detect_senders_from_html(html_files)

    if len(senders) < 2:
        print(f"Warning: Only {len(senders)} sender(s) detected in HTML files")
        if len(senders) == 0:
            print("No senders found. Please check your HTML files.")
            return

    # Map detected senders to clients
    # Use default mappings from .env if available, otherwise use the top two senders
    from_name_1 = default_from_name_1 if default_from_name_1 else (
        senders[0] if senders else None)
    from_name_2 = default_from_name_2 if default_from_name_2 else (
        senders[1] if len(senders) > 1 else None)

    print(f"Sender 1: {from_name_1} -> will use client 1")
    if from_name_2:
        print(f"Sender 2: {from_name_2} -> will use client 2")
    print(f"All other senders will use client 1 by default")

    for html_file in html_files:
        file_path = os.path.join(export_folder, html_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        messages = soup.find_all('div', class_='message')
        for msg in messages:
            # Determine sender based on from_name
            from_name_tag = msg.find('div', class_='from_name')
            from_name = from_name_tag.get_text(
                strip=True) if from_name_tag else ""

            if from_name == from_name_2:
                current_client = client2
                current_entity = group_entity2
            else:
                # Default to client1 for all other senders including from_name_1
                current_client = client1
                current_entity = group_entity

            date = msg.find('div', class_='date')
            message_time_raw = date['title'] if date and 'title' in date.attrs else None
            message_time = await process_time_format(message_time_raw)

            # Skip if time is invalid
            if message_time == "Unknown time":
                continue

            text = msg.find('div', class_='text')
            text_content = text.get_text(strip=True) if text else ""

            media_path = None
            media_caption = None
            media_tag = msg.find('a', class_='photo_wrap') or msg.find('a', class_='media_photo') \
                or msg.find('video') or msg.find('audio') or msg.find('a', class_='media_document')

            if media_tag:
                href = media_tag.get('href') or media_tag.get('src')
                if href:
                    media_path = os.path.join(export_folder, href)
                    if href.endswith('.tgs'):
                        media_caption = f"[{message_time}]"
                    elif 'photo' in href or href.endswith(('.jpg', '.jpeg', '.png')):
                        media_caption = f"[{message_time}]"
                    else:
                        media_caption = f"[{message_time}]"

            message_sent = False

            try:
                if media_path and os.path.exists(media_path):
                    await current_client.send_file(
                        current_entity,
                        media_path,
                        caption=media_caption or f"{text_content}\n[{message_time}]"
                    )
                    print(f"Media sent from {from_name}: {media_path}")
                    message_sent = True
                elif text_content:
                    await current_client.send_message(current_entity, f"{text_content}\n[{message_time}]")
                    print(f"Message sent from {from_name}: {text_content}")
                    message_sent = True
            except Exception as e:
                print(f"Error sending message from {from_name}: {e}")

            if message_sent:
                await asyncio.sleep(3)

    print("Completed sending messages and media!")
    await client1.disconnect()
    await client2.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
