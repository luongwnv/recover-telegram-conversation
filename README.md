# Telegram Message Importer

This script allows you to import messages from HTML files exported from Telegram into a Telegram group chat. It supports both text messages and media files.

## Features

* Import text messages and media files from Telegram HTML exports
* Support for multiple user accounts
* Preserves message timestamps
* Handles various media types (photos, videos, documents)
* **Automatic sender detection** from HTML files
* Optional manual sender mapping via environment variables

## Requirements

* Python 3.7+
* Telethon library
* BeautifulSoup4
* python-dotenv

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd telegram-message-importer
   ```
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following content:
   ```
   API_ID_1=your_api_id_1
   API_HASH_1=your_api_hash_1
   PHONE_1=your_phone_number_1

   API_ID_2=your_api_id_2
   API_HASH_2=your_api_hash_2
   PHONE_2=your_phone_number_2

   GROUP_CHAT_NAME=@your_group_chat_name

   # Optional - override automatic sender detection
   DEFAULT_FROM_NAME_1=primary_sender_name
   DEFAULT_FROM_NAME_2=secondary_sender_name
   ```

## How to Use

1. Get your API credentials from [my.telegram.org](https://my.telegram.org/)
2. Export your Telegram chat history and place the HTML files in the same directory as the script
3. Run the script:
   ```
   python main.py
   ```
4. When running for the first time, you'll need to authenticate each Telegram account by entering the verification code sent to your Telegram app

## How Sender Detection Works

The script automatically analyzes your HTML files to identify message senders:

1. It counts all unique sender names in the HTML files
2. The most frequent sender is assigned to client1
3. The second most frequent sender is assigned to client2
4. All other senders are handled by client1 by default

You can override this automatic detection by setting `DEFAULT_FROM_NAME_1` and `DEFAULT_FROM_NAME_2` in your `.env` file.

## File Structure

* `main.py` - The main script that handles the import process
* `requirements.txt` - List of required Python packages
* `.env` - Configuration file for API credentials and group chat name

## How It Works

1. The script reads HTML files exported from Telegram
2. It automatically identifies the sender names from the HTML files
3. It parses the messages and extracts text content, media files, and timestamps
4. It determines which client to use based on the sender's name
5. It sends each message to the specified group chat using the Telegram API
6. Messages are sent with a delay to avoid rate limiting

## Troubleshooting

* If you encounter authentication issues, delete the `session_user1` and `session_user2` files and run the script again
* Make sure your HTML exports and their media files are in the same directory as the script
* Check that your API credentials and phone numbers are correct in the `.env` file
* If the automatic sender detection isn't working as expected, you can manually set the `DEFAULT_FROM_NAME_1` and `DEFAULT_FROM_NAME_2` variables in your `.env` file

## Note

This script requires Telegram API access, which means you need to register your application on [my.telegram.org](https://my.telegram.org/).
