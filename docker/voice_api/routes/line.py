# import os
# from dotenv import load_dotenv
# from utils.mongodb import mongo_user_insert , mongo_user_list , mongo_device_list
# load_dotenv()
# from datetime import datetime ,timezone ,timedelta
# import time
# from threading import Thread

# from flask import request, abort, Blueprint
# import json

# from linebot import LineBotApi
# from linebot.exceptions import LineBotApiError
# from linebot.models import Profile , TextSendMessage

# from linebot.v3 import (
#     WebhookHandler
# )
# from linebot.v3.exceptions import (
#     InvalidSignatureError
# )
# from linebot.v3.messaging import (
#     Configuration,
#     ApiClient,
#     MessagingApi,
#     ReplyMessageRequest,
#     TextMessage,
# )
# from linebot.v3.webhooks import (
#     MessageEvent,
#     TextMessageContent
# )

# load_dotenv()

# line_blueprint = Blueprint('line', __name__)

# configuration = Configuration(access_token=os.environ['CHANNEL_ACCESS_TOKEN'])
# handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
# line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])  # Correct initialization

# def monitor_and_notify():
#     last_device = set()
#     while True:
#         try:
#             device_json = mongo_device_list()
#             if device_json:
#                 devices = json.loads(device_json)
#                 current_device = set(devices)
#                 if last_device and current_device != last_device:
#                     user_json = mongo_user_list()
#                     if user_json:
#                         users = json.loads(user_json)
#                         message = "your child is crying from\n"
#                         for device in current_device:
#                             if isinstance(device, dict) and 'device_id' in device:
#                                 message += f"device {device['device_id']}\n"
#                             else:
#                                 message += "Error with device data.\n"
#                         for user in users:
#                             if isinstance(user, dict) and 'user_id' in user:
#                                 try:
#                                     line_bot_api.push_message(
#                                         user['user_id'],
#                                         TextSendMessage(text=message)
#                                     )
#                                 except LineBotApiError as e:
#                                     print(f"Error sending message to user {user['user_id']}: {e}")
#                         last_device = current_device
            
#                  # Wait before next check
#                     time.sleep(30)  # Check every 30 seconds
            
#         except Exception as e:
#             print(f"Error in monitor_and_notify: {e}")
#             time.sleep(60)  # Wait longer if there's an error
    
# def start_monitoring():
#     monitor_thread = Thread(target=monitor_and_notify, daemon=True)
#     monitor_thread.start()

# @line_blueprint.before_app_first_request
# def before_first_request():
#     start_monitoring()

# @line_blueprint.route("/callback", methods=['POST'])
# def callback():
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     return 'OK'

# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     collect_user_command(event)
#     reply_text = create_reply(event.message.text)

#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text=reply_text)]
#             )
#         )

# def collect_user_command(event):
#     user_id = event.source.user_id
#     timestamp = event.timestamp
#     user_message = event.message.text
#     timestamp_int = int(timestamp)
#     covert_time = datetime.fromtimestamp(timestamp_int/1000 ,timezone.utc)
#     timezone_offset = timedelta(hours=7)
#     local_time = covert_time + timezone_offset
#     format_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
#     try:
#         profile = line_bot_api.get_profile(user_id)
#         display_name = profile.display_name
#         pic_url = profile.picture_url
#     except LineBotApiError as e:
#         display_name = "Unknown"
#         pic_url = None
#         print(f"Error fetching user profile: {e}")

#     # Prepare user data
#     user_data = {
#         'user_id': user_id,
#         'timestamp': format_time ,
#         'name': display_name,
#         'picture': pic_url,
#         'command': user_message
#     }
#     mongo_user_insert(user_data)

# def create_reply(user_message):
#     if user_message == "#list":
#         users_json = mongo_user_list()
#         if users_json:
#             users = json.loads(users_json)
#             reply_text = "Here are the rooms:\n"
#             for user in users:
#                 if isinstance(user, dict) and 'user_id' in user:
#                     reply_text += f"user {user['user_id']}\n"
#                 else:
#                     reply_text += "Error with user data.\n"
#         else:
#             reply_text = "Sorry, I couldn't find any users."
#     else:
#         reply_text = f"You said: {user_message}"

#     return reply_text

# import os
# from dotenv import load_dotenv
# from utils.mongodb import mongo_user_insert, mongo_user_list, mongo_device_list
# load_dotenv()

# from datetime import datetime, timezone, timedelta
# import time
# from threading import Thread
# from flask import request, abort, Blueprint
# import json
# from linebot import LineBotApi
# from linebot.exceptions import LineBotApiError
# from linebot.models import TextSendMessage

# from linebot.v3 import WebhookHandler
# from linebot.v3.exceptions import InvalidSignatureError
# from linebot.v3.messaging import (
#     Configuration,
#     ApiClient,
#     MessagingApi,
#     ReplyMessageRequest,
#     TextMessage,
# )
# from linebot.v3.webhooks import MessageEvent, TextMessageContent

# # Initialize environment variables
# configuration = Configuration(access_token=os.environ['CHANNEL_ACCESS_TOKEN'])
# handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
# line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])

# # Create Flask Blueprint
# line_blueprint = Blueprint('line', __name__)

# def monitor_and_notify():
#     """Monitors devices and notifies users of any changes."""
#     last_device = set()
#     while True:
#         try:
#             device_json = mongo_device_list()
#             if device_json:
#                 devices = json.loads(device_json)
#                 current_device = set(devices)
#                 if last_device and current_device != last_device:
#                     user_json = mongo_user_list()
#                     if user_json:
#                         users = json.loads(user_json)
#                         message = "Your child is crying from:\n"
#                         for device in current_device:
#                             if isinstance(device, dict) and 'device_id' in device:
#                                 message += f"Device {device['device_id']}\n"
#                             else:
#                                 message += "Error with device data.\n"
#                         for user in users:
#                             if isinstance(user, dict) and 'user_id' in user:
#                                 try:
#                                     line_bot_api.push_message(
#                                         user['user_id'],
#                                         TextSendMessage(text=message)
#                                     )
#                                 except LineBotApiError as e:
#                                     print(f"Error sending message to user {user['user_id']}: {e}")
#                         last_device = current_device
#             time.sleep(30)  # Check every 30 seconds
#         except Exception as e:
#             print(f"Error in monitor_and_notify: {e}")
#             time.sleep(60)  # Wait longer if there's an error

# def start_monitoring():
#     """Starts the monitoring thread."""
#     monitor_thread = Thread(target=monitor_and_notify, daemon=True)
#     monitor_thread.start()

# def register_blueprint(app):
#     """Registers app-specific logic for the LINE blueprint."""
#     @app.before_first_request
#     def before_first_request():
#         start_monitoring()

# @line_blueprint.route("/callback", methods=['POST'])
# def callback():
#     """Handles LINE webhook callbacks."""
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)
#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         abort(400)
#     return 'OK'

# @handler.add(MessageEvent, message=TextMessageContent)
# def handle_message(event):
#     """Handles user messages and sends appropriate replies."""
#     collect_user_command(event)
#     reply_text = create_reply(event.message.text)

#     with ApiClient(configuration) as api_client:
#         line_bot_api = MessagingApi(api_client)
#         line_bot_api.reply_message_with_http_info(
#             ReplyMessageRequest(
#                 reply_token=event.reply_token,
#                 messages=[TextMessage(text=reply_text)]
#             )
#         )

# def collect_user_command(event):
#     """Collects and stores user command data."""
#     user_id = event.source.user_id
#     timestamp = event.timestamp
#     user_message = event.message.text
#     timestamp_int = int(timestamp)
#     convert_time = datetime.fromtimestamp(timestamp_int / 1000, timezone.utc)
#     timezone_offset = timedelta(hours=7)
#     local_time = convert_time + timezone_offset
#     format_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
#     try:
#         profile = line_bot_api.get_profile(user_id)
#         display_name = profile.display_name
#         pic_url = profile.picture_url
#     except LineBotApiError as e:
#         display_name = "Unknown"
#         pic_url = None
#         print(f"Error fetching user profile: {e}")

#     # Prepare user data
#     user_data = {
#         'user_id': user_id,
#         'timestamp': format_time,
#         'name': display_name,
#         'picture': pic_url,
#         'command': user_message
#     }
#     mongo_user_insert(user_data)

# def create_reply(user_message):
#     """Generates a reply based on the user's message."""
#     if user_message == "#list":
#         users_json = mongo_user_list()
#         if users_json:
#             users = json.loads(users_json)
#             reply_text = "Here are the users:\n"
#             for user in users:
#                 if isinstance(user, dict) and 'user_id' in user:
#                     reply_text += f"User {user['user_id']}\n"
#                 else:
#                     reply_text += "Error with user data.\n"
#         else:
#             reply_text = "Sorry, I couldn't find any users."
#     else:
#         reply_text = f"You said: {user_message}"
#     return reply_text

import os
from dotenv import load_dotenv
from utils.mongodb import mongo_user_insert, mongo_user_list, mongo_device_list
load_dotenv()

from datetime import datetime, timezone, timedelta
import time
from threading import Thread
from flask import request, abort, Blueprint
import json
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# Initialize environment variables
configuration = Configuration(access_token=os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])

# Create Flask Blueprint
line_blueprint = Blueprint('line', __name__)

def monitor_and_notify():
    """Monitors devices and notifies users of any changes."""
    last_device = set()
    while True:
        try:
            device_json = mongo_device_list()
            if device_json:
                devices = json.loads(device_json)
                current_device = set(devices)
                if last_device and current_device != last_device:
                    user_json = mongo_user_list()
                    if user_json:
                        users = json.loads(user_json)
                        message = "Your child is crying from:\n"
                        for device in current_device:
                            if isinstance(device, dict) and 'device_id' in device:
                                message += f"Device {device['device_id']}\n"
                            else:
                                message += "Error with device data.\n"
                        for user in users:
                            if isinstance(user, dict) and 'user_id' in user:
                                try:
                                    line_bot_api.push_message(
                                        user['user_id'],
                                        TextSendMessage(text=message)
                                    )
                                except LineBotApiError as e:
                                    print(f"Error sending message to user {user['user_id']}: {e}")
                        last_device = current_device
            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            print(f"Error in monitor_and_notify: {e}")
            time.sleep(60)  # Wait longer if there's an error

@line_blueprint.route("/callback", methods=['POST'])
def callback():
    """Handles LINE webhook callbacks."""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    """Handles user messages and sends appropriate replies."""
    collect_user_command(event)
    reply_text = create_reply(event.message.text)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

def collect_user_command(event):
    """Collects and stores user command data."""
    user_id = event.source.user_id
    timestamp = event.timestamp
    user_message = event.message.text
    timestamp_int = int(timestamp)
    convert_time = datetime.fromtimestamp(timestamp_int / 1000, timezone.utc)
    timezone_offset = timedelta(hours=7)
    local_time = convert_time + timezone_offset
    format_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        profile = line_bot_api.get_profile(user_id)
        display_name = profile.display_name
        pic_url = profile.picture_url
    except LineBotApiError as e:
        display_name = "Unknown"
        pic_url = None
        print(f"Error fetching user profile: {e}")

    # Prepare user data
    user_data = {
        'user_id': user_id,
        'timestamp': format_time,
        'name': display_name,
        'picture': pic_url,
        'command': user_message
    }
    mongo_user_insert(user_data)

def create_reply(user_message):
    """Generates a reply based on the user's message."""
    if user_message == "#list":
        users_json = mongo_user_list()
        if users_json:
            users = json.loads(users_json)
            reply_text = "Here are the users:\n"
            for user in users:
                if isinstance(user, dict) and 'user_id' in user:
                    reply_text += f"User {user['user_id']}\n"
                else:
                    reply_text += "Error with user data.\n"
        else:
            reply_text = "Sorry, I couldn't find any users."
    else:
        reply_text = f"You said: {user_message}"
    return reply_text
