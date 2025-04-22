# --- START OF FILE VideoFlux-Re-master/bot/start.py ---

from config.config import Config
# REMOVED: Telethon Button import
# from telethon import events, Button
# ADDED: Pyrogram imports
from pyrogram import filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot_helper.Others.Helper_Functions import getbotuptime, get_config, delete_trash, get_logs_msg, gen_random_string, get_readable_time, get_human_size, botStartTime, get_current_time, get_env_keys, export_env_file, get_env_dict, get_host_stats
from os.path import exists
from asyncio import sleep as asynciosleep
from os import execl, makedirs, remove
from os.path import isdir, isfile
from sys import argv, executable
from bot_helper.Aria2.Aria2_Engine import Aria2, getDownloadByGid
from bot_helper.Process.Process_Status import ProcessStatus
from time import time
from asyncio import create_task
from bot_helper.Database.User_Data import get_data, new_user, change_task_limit, get_task_limit, saveoptions
from bot_helper.Telegram.Telegram_Client import Telegram
from bot_helper.Process.Running_Tasks import add_task, get_status_message, get_user_id, get_queued_tasks_len, refresh_tasks, remove_from_working_task, get_ffmpeg_log_file
from bot_helper.Process.Running_Process import remove_running_process
from asyncio import Lock
from psutil import virtual_memory, cpu_percent, disk_usage
from bot_helper.Others.Names import Names
# REMOVED: Telethon error import
# from telethon.errors.rpcerrorlist import MessageIdInvalidError
# ADDED: Pyrogram error import
from pyrogram.errors import MessageNotModified, MessageIdInvalid
from re import findall
from requests import get
from bot_helper.Others.SpeedTest import speedtest
from subprocess import run as srun
# REMOVED: Heroku import


status_update = {}
status_update_lock = Lock()


if not isdir('./userdata'):
    makedirs("./userdata")





#////////////////////////////////////Variables////////////////////////////////////#
sudo_users = Config.SUDO_USERS
owner_id = Config.OWNER_ID
allowed_chats = Config.ALLOWED_CHATS
auth_chat = Config.AUTH_GROUP_ID
# REMOVED: Telethon client variable
# TELETHON_CLIENT = Telegram.TELETHON_CLIENT
# ADDED: Pyrogram client variable
PYROGRAM_CLIENT = Telegram.PYROGRAM_CLIENT
LOGGER = Config.LOGGER
SAVE_TO_DATABASE = Config.SAVE_TO_DATABASE

#////////////////////////////////////Functions////////////////////////////////////#

# REMOVED: hardmux_multi_task function
# REMOVED: append_multi_task function
# REMOVED: multi_tasks function


###############------Create_Dire------###############
def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return

###############------Check_File------###############
def check_file(loc, file_name):
    if isfile(f"{loc}/{file_name}"):
        return f"{loc}/{gen_random_string(5)}_{file_name}"
    else:
        return f"{loc}/{file_name}"

###############------Download_From_Direct_Link------###############
def dw_file_from_url(url, filename):
        r = get(url, allow_redirects=True, stream=True)
        with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024 * 10):
                        if chunk:
                                fd.write(chunk)
        return

###############------Download_Rclone_Config------###############
for user_id in get_data():
    link = get_data().get(user_id, {}).get('rclone_config_link', False) # MODIFIED: Use .get()
    if link:
        LOGGER.info(f"🔽Downloading Rclone Config For User_ID {user_id} From Link {link}")
        r_config = f'./userdata/{str(user_id)}_rclone.conf'
        try:
            dw_file_from_url(link, r_config)
        except Exception as e:
            LOGGER.info(f"❗Error While Downloading Rclone Config For User_ID {user_id} From Link {link}")
    else:
        LOGGER.info(f"🟡Rclone Config Link Not Found For User_ID {user_id}")


###############------Check_Magenet------###############
def is_magnet(url: str):
    magnet = findall(r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*", url)
    return bool(magnet)



#////////////////////////////////////Telethon Functions////////////////////////////////////#
# MODIFIED: Renamed section as functions are now Pyrogram-based

###############------Mention_User------###############
# MODIFIED: Use Pyrogram event structure
def get_mention(message): # Changed event to message
    return f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

###############------Check_File_Or_URL_Event------###############
# MODIFIED: Use Pyrogram message structure
async def get_url_from_message(message): # Changed new_event to message
        if message.document or message.video or message.audio: # Check for media types
            return message # Return the message object itself
        elif message.text:
            return str(message.text) # Return text if no media
        return None # Return None if neither media nor text

###############------Get_Username------###############
# MODIFIED: Use Pyrogram event structure
def get_username(message): # Changed event to message
    try:
        if message.from_user.username:
            user_name = message.from_user.username
        else:
            user_name = False
    except:
            user_name = False
    return user_name

###############------Check_Auth_User------###############
# MODIFIED: Use Pyrogram message structure
def user_auth_checker(message): # Changed event to message
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.chat.type == message.chat.type.PRIVATE: # Check private chat
        if user_id == owner_id:
            return True
    else: # Group/Supergroup/Channel
        if user_id in sudo_users or user_id in allowed_chats or user_id == owner_id or chat_id == auth_chat:
            return True
    return False

###############------Check_Sudo_User_Event------###############
# MODIFIED: Use Pyrogram message structure
def sudo_user_checker_event(message): # Changed event to message
    if message.from_user.id in sudo_users or message.from_user.id == owner_id:
            return True
    return False

###############------Check_Sudo_User_ID------###############
def sudo_user_checker_id(user_id):
    if user_id in sudo_users or user_id == owner_id:
            return True
    return False

###############------Check_Owner_User_Event------###############
# MODIFIED: Use Pyrogram message structure
def owner_checker(message): # Changed event to message
    if message.from_user.id == owner_id:
            return True
    return False

###############------Get_Link------###############
# MODIFIED: Use Pyrogram message structure and client
async def get_link(client, message): # Added client, changed event to message
    custom_file_name = False
    text = message.text if message.text else "" # Get text safely
    if "|" in text:
        ext_data = text.split('|')
        custom_file_name = str(ext_data[-1]).strip()
        commands = ext_data[0].strip().split(' ')
    else:
        commands = text.split(' ')
    if len(commands) >= 2: # Check >= 2 for command + link
            if str(commands[1]).startswith("http") or is_magnet(commands[1]):
                return commands[1], custom_file_name
            else:
                # Check if it's just the command (like /merge) without a link
                if len(commands) == 1 and commands[0].startswith('/'):
                     pass # Let the reply check handle it
                else:
                    return "invalid", custom_file_name

    if message.reply_to_message:
        msg_object = message.reply_to_message
        if msg_object.document or msg_object.video or msg_object.audio: # Check media
            return msg_object, custom_file_name # Return message object
        elif msg_object.text: # Check text in replied message
            if str(msg_object.text).startswith("http") or is_magnet(str(msg_object.text)):
                return str(msg_object.text), custom_file_name
            else:
                return "invalid", custom_file_name
        else: # Replied message has no usable content
             return "invalid", custom_file_name
    else: # No link in command and no reply
        return False, custom_file_name


###############------Ask_User_ID------###############
# MODIFIED: Use Pyrogram message structure
async def get_sudo_user_id(message): # Changed event to message
    if message.reply_to_message:
        reply_data = message.reply_to_message
        return reply_data.from_user.id
    return False


###############------Get_Custom_Name------###############
# MODIFIED: Use Pyrogram message structure
async def get_custom_name(message): # Changed event to message
    custom_file_name = False
    text = message.text if message.text else ""
    if "|" in text:
        ext_data = text.split('|')
        custom_file_name = str(ext_data[-1]).strip()
    return custom_file_name

# MODIFIED: Needs complete rewrite for Pyrogram conversations
###############------Ask_Text------###############
async def ask_text(client, chat_id, user_id, event_message, timeout, message, text_type, include_list=False):
    # Placeholder - Pyrogram conversation logic is different
    await event_message.reply(f"Text input ({message}) needs adaptation for Pyrogram.")
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs complete rewrite for Pyrogram conversations
###############------Ask_Text_Event------###############
async def ask_text_event(client, chat_id, user_id, event_message, timeout, message, message_hint=False):
    # Placeholder - Pyrogram conversation logic is different
    await event_message.reply(f"Text input ({message}) needs adaptation for Pyrogram.")
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs complete rewrite for Pyrogram conversations
###############------Ask_Text_List------###############
async def ask_text_list(client, chat_id, user_id, event_message, timeout, message, include_list):
    # Placeholder - Pyrogram conversation logic is different
    await event_message.reply(f"Text list input ({message}) needs adaptation for Pyrogram.")
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs complete rewrite for Pyrogram conversations
###############------Ask Media OR URL------###############
async def ask_media_OR_url(client, event_message, chat_id, user_id, keywords, message, timeout, mtype, s_handle, allow_magnet=True, allow_url=True, message_hint=False, allow_command=False, stop_on_url=True):
    # Placeholder - Pyrogram conversation logic is different
    await event_message.reply(f"Media/URL input ({message}) needs adaptation for Pyrogram.")
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs complete rewrite for Pyrogram conversations
###############------Ask URL------###############
async def ask_url(client, event_message, chat_id, user_id, keywords, message, timeout, s_handle, allow_magnet=True, allow_url=True, message_hint=False, allow_command=False, stop_on_url=True):
    # Placeholder - Pyrogram conversation logic is different
    await event_message.reply(f"URL input ({message}) needs adaptation for Pyrogram.")
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# REMOVED: get_thumbnail function (Static handled by ProcessStatus init)

# REMOVED: ask_watermark function

# REMOVED: ask_thumbnail function


# MODIFIED: Use Pyrogram message structure and client
async def update_status_message(client, message): # Added client, changed event to message
        reply = await message.reply_text("⏳Please Wait") # Use reply_text
        chat_id = message.chat.id
        user_id = message.from_user.id
        status_update_id = gen_random_string(5)
        async with status_update_lock:
            if chat_id not in status_update:
                status_update[chat_id] = {}
            status_update[chat_id].clear()
            status_update[chat_id]['update_id'] = status_update_id
        await asynciosleep(2)
        while True:
            status_message = await get_status_message(reply) # Pass Pyrogram message object
            if not status_message:
                try:
                    # Use edit_text for Pyrogram
                    await reply.edit_text(f"No Running Process!\n\n**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}")
                except MessageNotModified: # Catch Pyrogram specific error
                    pass
                except Exception as e: # Catch other potential errors
                    LOGGER.error(f"Error editing status message (no process): {e}")
                    # Fallback reply if edit fails
                    await message.reply_text(f"No Running Process!\n\n**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}")
                break
            if chat_id not in status_update or status_update[chat_id]['update_id'] != status_update_id: # Check if chat_id exists
                try:
                    await reply.delete()
                except Exception as e:
                    LOGGER.warning(f"Failed to delete status message: {e}")
                break
            if get_data().get(user_id, {}).get('show_stats', True): # MODIFIED: Use .get()
                status_message += f"**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}"
                status_message += f"\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n"
            if get_data().get(user_id, {}).get('show_time', True): # MODIFIED: Use .get()
                    status_message+= "**Current Time:** " + get_current_time() + "\n"
            status_message += f"**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}"
            try:
                 # Use edit_text and InlineKeyboardMarkup for Pyrogram
                await reply.edit_text(status_message, reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('⭕ Close', callback_data='close_settings')]
                        ]))
            except MessageNotModified: # Catch Pyrogram specific error
                 pass
            except MessageIdInvalid: # Catch if message was deleted
                 LOGGER.warning("Status message ID invalid, likely deleted.")
                 break
            except Exception as e:
                LOGGER.info(f"Status Update Error: {str(e)}")
            await asynciosleep(get_data().get(user_id, {}).get('update_time', 7)) # MODIFIED: Use .get()
        LOGGER.info(f"Status Updating Complete")
        return


# MODIFIED: Use Pyrogram client and message
###############------Save_Rclone_Config------###############
@PYROGRAM_CLIENT.on_message(filters.command("saveconfig") & filters.private) # Use Pyrogram filters
async def _saverclone(client, message): # Use Pyrogram arguments
        user_id = message.from_user.id
        chat_id = message.chat.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        r_config = f'./userdata/{str(user_id)}_rclone.conf'
        check_config = exists(r_config)
        link = False
        if check_config:
                text = f"Rclone Config Already Present\n\nSend Me New Config To Replace."
        else:
                text = f"Rclone Config Not Present\n\nSend Me Config To Save."
        # MODIFIED: Needs adaptation for Pyrogram
        # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/saveconfig", "stop"], text, 120, "text/", True, False)
        await message.reply_text("Rclone config saving needs adaptation for Pyrogram conversations.") # Placeholder
        new_event = None # Placeholder
        if new_event and new_event not in ["cancelled", "stopped"]:
            if new_event.document: # Check document for Pyrogram
                await client.download_media(new_event.document, file_name=r_config) # Use client.download_media
            elif new_event.text: # Check text for Pyrogram
                link = str(new_event.text)
                dw_file_from_url(link, r_config)
                await saveoptions(user_id, 'rclone_config_link', link, SAVE_TO_DATABASE)
            if not exists(r_config):
                await message.reply_text("❌Failed To Download Config File.") # Use reply_text
                return
            accounts = await get_config(r_config)
            if not accounts:
                await delete_trash(r_config)
                await message.reply_text("❌Invalid Config File Or Empty Config File.")
                return
            await saveoptions(user_id, 'drive_name', accounts[0], SAVE_TO_DATABASE)
            if link:
                await saveoptions(user_id, 'rclone_config_link', link, SAVE_TO_DATABASE)
            await message.reply_text(f"✅Config Saved Successfully\n\n🔶Using {str(get_data().get(user_id, {}).get('drive_name', 'N/A'))} Drive For Uploading.") # Use reply_text
        return


# MODIFIED: Use Pyrogram client and message
###############------Change_Task_Limit------###############
@PYROGRAM_CLIENT.on_message(filters.command("tasklimit") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _changetasklimit(client, message): # Use Pyrogram arguments
        user_id = message.from_user.id
        chat_id = message.chat.id
        # MODIFIED: Needs adaptation for Pyrogram
        # limit = await ask_text(client, chat_id, user_id, message, 120, "Send New Task Limit", int)
        await message.reply_text("Task limit changing needs adaptation for Pyrogram conversations.") # Placeholder
        limit = None # Placeholder
        if limit:
            change_task_limit(int(limit))
            await refresh_tasks()
            await message.reply_text(f'✅Successfully Set New Limit: {get_task_limit()}') # Use reply_text
            return


# MODIFIED: Use Pyrogram client and message
###############------Restart------###############
@PYROGRAM_CLIENT.on_message(filters.command("restart") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _restart(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        reply = await message.reply_text("♻Restarting...") # Use reply_text
        srun(["pkill", "-f", "aria2c|ffmpeg|rclone"])
        srun(["python3", "update.py"])
        with open(".restartmsg", "w") as f:
                f.truncate(0)
                f.write(f"{chat_id}\n{reply.id}\n") # Use reply.id (Pyrogram)
        execl(executable, executable, *argv)


# REMOVED: Heroku restart handler

# MODIFIED: Use Pyrogram client and message
###############------Get_Logs_Message------###############
@PYROGRAM_CLIENT.on_message(filters.command("log") & filters.private & filters.user(sudo_users + [owner_id])) # Use Pyrogram filters
async def _log(client, message): # Use Pyrogram arguments
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        log_file = "Logging.txt"
        if exists(log_file):
                # Send log content directly if too long for a single message
                log_content = str(get_logs_msg(log_file))
                if len(log_content) > 4096:
                     await message.reply_document(log_file) # Send as document if too long
                else:
                     await message.reply_text(log_content) # Use reply_text
        else:
            await message.reply_text("❗Log File Not Found")
        return


# MODIFIED: Use Pyrogram client and message
###############------Get_Log_File------###############
@PYROGRAM_CLIENT.on_message(filters.command("logs") & filters.private & filters.user(sudo_users + [owner_id])) # Use Pyrogram filters
async def _logs(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        log_file = "Logging.txt"
        if exists(log_file):
            try:
                await client.send_document(chat_id, document=log_file) # Use send_document
            except Exception as e:
                await message.reply_text(str(e))
        else:
            await message.reply_text("❗Log File Not Found")
        return


# MODIFIED: Use Pyrogram client and message
###############------Reset_Database------###############
@PYROGRAM_CLIENT.on_message(filters.command("resetdb") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _resetdb(client, message): # Use Pyrogram arguments
        await message.reply_text("*️⃣Are you sure?\n\n🚫 This will reset your all database 🚫", reply_markup=InlineKeyboardMarkup([ # Use Pyrogram InlineKeyboardMarkup
                [InlineKeyboardButton('Yes 🚫', callback_data='resetdb_True')],
                [InlineKeyboardButton('No 😓', callback_data='resetdb_False')],
                [InlineKeyboardButton('⭕Close', callback_data='close_settings')]
            ]))
        return

# REMOVED: Save Watermark handler

# MODIFIED: Use Pyrogram client and message
###############------Save_Thumbnail------###############
@PYROGRAM_CLIENT.on_message(filters.command("savethumb") & filters.private) # Use Pyrogram filters
async def _savethumb(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        # MODIFIED: Replaced ask_thumbnail logic with simple file download
        Thumbnail_path = f'./userdata/{str(user_id)}_Thumbnail.jpg'
        Thumbnail_check = exists(Thumbnail_path)
        if Thumbnail_check:
                text = f"Thumbnail Already Present\n\n🔷Send Me New Thumbnail To Replace."
        else:
                text = f"Thumbnail Not Present\n\n🔶Send Me Thumbnail To Save."
        # MODIFIED: Needs adaptation for Pyrogram
        # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/savethumb", "stop"], text, 120, "image/", True, False, False)
        await message.reply_text("Thumbnail saving needs adaptation for Pyrogram conversations.") # Placeholder
        new_event = None # Placeholder
        if new_event and new_event not in ["cancelled", "stopped"]:
            await client.download_media(new_event.photo or new_event.document, file_name=Thumbnail_path) # Check photo or document
            if exists(Thumbnail_path):
                 await message.reply_text("✅Thumbnail saved successfully.")
                 return True # Indicate success
            else:
                 await message.reply_text("❗Failed To Save Thumbnail.")
                 return False # Indicate failure
        else:
            # Handle cancellation or timeout if needed, maybe just return False
            return False


# MODIFIED: Use Pyrogram client and message
###############------Renew------###############
@PYROGRAM_CLIENT.on_message(filters.command("renew") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _renew(client, message): # Use Pyrogram arguments
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        await message.reply_text("*️⃣Are you sure?\n\n🚫 This will delete all your downloads and saved watermark locally 🚫", reply_markup=InlineKeyboardMarkup([ # Use Pyrogram InlineKeyboardMarkup
                [InlineKeyboardButton('Yes 🚫', callback_data='renew_True')],
                [InlineKeyboardButton('No 😓', callback_data='renew_False')],
                [InlineKeyboardButton('⭕Close', callback_data='close_settings')]
            ]))
        return

# MODIFIED: Use Pyrogram client and message
###############------Save_Stats------###############
@PYROGRAM_CLIENT.on_message(filters.command("stats") & filters.private & filters.user(sudo_users + [owner_id])) # Use Pyrogram filters
async def _stats_msg(client, message): # Use Pyrogram arguments
    await message.reply_text(str(await get_host_stats()), parse_mode='html') # Use reply_text
    return


# MODIFIED: Use Pyrogram client and message
###############------Speed_Test------###############
@PYROGRAM_CLIENT.on_message(filters.command("speedtest") & filters.private & filters.user(sudo_users + [owner_id])) # Use Pyrogram filters
async def _speed_test(client, message): # Use Pyrogram arguments
    chat_id = message.chat.id
    reply = await message.reply_text("⏳Running Speed Test, Please Wait.....")
    try:
        file_path, caption = await speedtest()
        await client.send_photo(chat_id, photo=file_path, caption=caption, reply_to_message_id=message.id) # Use send_photo
    except Exception as e:
        await message.reply_text(str(e))
    await reply.delete()
    return


# MODIFIED: Use Pyrogram client and message
###############------Start_Message------###############
@PYROGRAM_CLIENT.on_message(filters.command("start") & filters.private) # Use Pyrogram filters
async def _startmsg(client, message): # Use Pyrogram arguments
    text = f"Hi {get_mention(message)}, I Am Alive." # Use Pyrogram mention
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup([ # Use Pyrogram InlineKeyboardMarkup
        [InlineKeyboardButton('⭐ Bot By 𝚂𝚊𝚑𝚒𝚕 ⭐', url='https://t.me/nik66')],
        [InlineKeyboardButton('❤ Join Channel ❤', url='https://t.me/nik66x')]
    ]))
    return

# MODIFIED: Use Pyrogram client and message
###############------Bot_UpTime------###############
@PYROGRAM_CLIENT.on_message(filters.command("time") & filters.private & filters.user(sudo_users + [owner_id])) # Use Pyrogram filters
async def _timecmd(client, message): # Use Pyrogram arguments
    await message.reply_text(f'♻Bot Is Alive For {getbotuptime()}')
    return


# MODIFIED: Use Pyrogram client and message
###############------Cancel Process------###############
@PYROGRAM_CLIENT.on_message(filters.command("cancel") & filters.private) # Use Pyrogram filters
async def _cancel(client, message): # Use Pyrogram arguments
        user_id = message.from_user.id
        commands = message.text.split(' ') # Use message.text
        if len(commands)==3:
                processx = commands[1]
                process_id = commands[2]
                try:
                        if processx=="aria":
                            if dl := getDownloadByGid(process_id):
                                if dl.listener().user_id==user_id or user_id==owner_id:
                                    await Aria2.cancel_download(process_id)
                                    await remove_from_working_task(dl.listener().process_id)
                                else:
                                    await message.reply_text(f'❗You Have No Permission To Cancel This Task')
                                    return
                            else:
                                await message.reply_text(f'❗No download with this id')
                                return
                        elif processx=="process":
                            add_user_id = get_user_id(process_id)
                            if add_user_id:
                                if add_user_id==user_id or user_id==owner_id:
                                    cancel_result = await remove_running_process(process_id)
                                    await remove_from_working_task(process_id)
                                    if not cancel_result:
                                            await message.reply_text(f'❗No process with this id')
                                            return
                                else:
                                    await message.reply_text(f'❗You Have No Permission To Cancel This Task')
                                    return
                            else:
                                if user_id==owner_id:
                                    cancel_result = await remove_running_process(process_id)
                                    await remove_from_working_task(process_id)
                                    if not cancel_result:
                                            await message.reply_text(f'❗No process with this id')
                                            return
                                else:
                                    await message.reply_text(f'❗You Have No Permission To Cancel This Task')
                                    return
                        await message.reply_text(f'✅Successfully Cancelled.')
                except Exception as e:
                        await message.reply_text(str(e))
                return
        else:
                await message.reply_text(f'❗Give Me Process ID To Cancel.')
        return


# MODIFIED: Use Pyrogram client and message
###############------FFMPEF Log------###############
@PYROGRAM_CLIENT.on_message(filters.command("ffmpeg") & filters.private) # Use Pyrogram filters
async def _ffmpeg_log(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        commands = message.text.split(' ') # Use message.text
        if len(commands)==3:
                processx = commands[1]
                process_id = commands[2]
                try:
                        if processx=="log":
                            log_file = await get_ffmpeg_log_file(process_id)
                            if log_file:
                                await client.send_document(chat_id, document=log_file) # Use send_document
                            else:
                                await message.reply_text("❗Log File Not Found")
                except Exception as e:
                        await message.reply_text(str(e))
                return
        else:
                await message.reply_text(f'❗Give Me Process ID.')
        return

# REMOVED: Compress handler

# MODIFIED: Use Pyrogram client and message
###############------Status------###############
@PYROGRAM_CLIENT.on_message(filters.command("status") & filters.private) # Use Pyrogram filters
async def _status(client, message): # Use Pyrogram arguments
        reply = await message.reply_text("⏳Please Wait")
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        status_update_id = gen_random_string(5)
        async with status_update_lock:
            if chat_id not in status_update:
                status_update[chat_id] = {}
            status_update[chat_id].clear()
            status_update[chat_id]['update_id'] = status_update_id
        await asynciosleep(2)
        while True:
            status_message = await get_status_message(reply)
            if not status_message:
                try:
                    await reply.edit_text(f"No Running Process!\n\n**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}")
                except MessageNotModified:
                    pass
                except Exception as e:
                    LOGGER.error(f"Error editing status message (no process): {e}")
                    await message.reply_text(f"No Running Process!\n\n**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}")
                break
            if chat_id not in status_update or status_update[chat_id]['update_id'] != status_update_id:
                try:
                    await reply.delete()
                except Exception as e:
                     LOGGER.warning(f"Failed to delete status message: {e}")
                break
            if get_data().get(user_id, {}).get('show_stats', True):
                status_message += f"**CPU:** {cpu_percent()}% | **FREE:** {get_human_size(disk_usage('/').free)}"
                status_message += f"\n**RAM:** {virtual_memory().percent}% | **UPTIME:** {get_readable_time(time() - botStartTime)}\n"
            if get_data().get(user_id, {}).get('show_time', True):
                    status_message+= "**Current Time:** " + get_current_time() + "\n"
            status_message += f"**QUEUED:** {get_queued_tasks_len()} | **TASK LIMIT:** {get_task_limit()}"
            try:
                await reply.edit_text(status_message, reply_markup=InlineKeyboardMarkup([ # Use Pyrogram InlineKeyboardMarkup
                        [InlineKeyboardButton('⭕ Close', callback_data='close_settings')]
                        ]))
            except MessageNotModified:
                 pass
            except MessageIdInvalid:
                 LOGGER.warning("Status message ID invalid, likely deleted.")
                 break
            except Exception as e:
                LOGGER.info(f"Status Update Error: {str(e)}")
            await asynciosleep(get_data().get(user_id, {}).get('update_time', 7))
        LOGGER.info(f"Status Updating Complete")
        return


# MODIFIED: Use Pyrogram client and message
###############------Settings------###############
@PYROGRAM_CLIENT.on_message(filters.command("settings") & filters.private) # Use Pyrogram filters
async def _settings(client, message): # Use Pyrogram arguments
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        text = f"⚙ Hi {get_mention(message)} Choose Your Settings" # Use Pyrogram mention
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup([ # Use Pyrogram InlineKeyboardMarkup
            [InlineKeyboardButton('#️⃣ General', callback_data='general_settings')],
            # [InlineKeyboardButton('❣ Telegram', callback_data='telegram_settings')], # REMOVED
            [InlineKeyboardButton('📝 Progress Bar', callback_data='progress_settings')],
            [InlineKeyboardButton('🍧 Merge', callback_data='merge_settings')],
            [InlineKeyboardButton('💻 Encode', callback_data='convert_settings')],
            [InlineKeyboardButton('🎬 Video ', callback_data='video_settings')],
            [InlineKeyboardButton('🔊 Audio', callback_data='audio_settings')],
            [InlineKeyboardButton('❤ VBR / 🖤CRF', callback_data='vbrcrf_settings')],
            [InlineKeyboardButton('🚍 HardMux', callback_data='hardmux_settings')],
            [InlineKeyboardButton('🎮 SoftMux', callback_data='softmux_settings')],
            [InlineKeyboardButton('⭕Close Settings', callback_data='close_settings')]
        ]))
        return

# REMOVED: Watermark handler

# MODIFIED: Use Pyrogram client and message
###############------Merge_Videos------###############
@PYROGRAM_CLIENT.on_message(filters.command("merge") & filters.private) # Use Pyrogram filters
async def _merge_videos(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        custom_file_name = await get_custom_name(message)
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.merge, custom_file_name) # Pass message
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        file_index = 1
        Cancel = False
        while True:
            # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/merge", "stop", "cancel"], f"Send Video or URL No {file_index}", 120, "video/", False, message_hint=f"🔷Send `stop` To Process Merge\n🔷Send `cancel` To Cancel Merge Process", allow_command=True)
            await message.reply_text(f"Merge input (file {file_index}) needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = "stopped" # Placeholder to stop loop for now
            if new_event and new_event not in ["cancelled", "stopped", "pass"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
                if type(link)==str:
                    task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
                else:
                    task['functions'].append(["TG", [link]])
                file_index+=1
            elif new_event=="stopped":
                break
            elif new_event=="cancelled":
                Cancel = True
                break
            elif not new_event:
                Cancel = True
                break
        if Cancel:
            del process_status
            return
        if len(task['functions'])<2:
            del process_status
            await message.reply_text("❗Atleast 2 Files Required To Merge")
            return
        # REMOVED: get_thumbnail call
        # REMOVED: Multi-task logic
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return


# MODIFIED: Use Pyrogram client and message
###############------SoftMux------###############
@PYROGRAM_CLIENT.on_message(filters.command("softmux") & filters.private) # Use Pyrogram filters
async def _softmux_subtitles(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/softmux", "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Softmux video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.softmux, custom_file_name) # Pass message
        file_index = 1
        Cancel = False
        while True:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/softmux", "stop", "cancel"], f"Send Subtitle SRT File No {file_index}", 120, False, False, message_hint=f"🔷Send `stop` To Process SoftMux\n🔷Send `cancel` To Cancel SoftMux Process", allow_command=True, allow_magnet=False, allow_url=False, stop_on_url=False)
            await message.reply_text(f"Softmux subtitle input (file {file_index}) needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = "stopped" # Placeholder to stop loop for now
            if new_event and new_event not in ["cancelled", "stopped", "pass"]:
                if new_event.document: # Check document
                    # Mime type check might need adjustment based on Pyrogram attributes
                    # if not str(new_event.document.mime_type).startswith("video/") and not str(new_event.document.mime_type).startswith("image/"):
                    if new_event.document.file_size < 512000: # Check size
                        sub_name = new_event.document.file_name
                        create_direc(f"{process_status.dir}/subtitles")
                        sub_dw_loc = check_file(f"{process_status.dir}/subtitles", sub_name)
                        sub_path = await client.download_media(new_event.document, file_name=sub_dw_loc) # Use client.download_media
                        process_status.append_subtitles(sub_path)
                        file_index+=1
                    else:
                        await message.reply_text("❌Subtitle Size Is More Than 500KB, Is This Really A Subtitle File")
                    # else:
                    #     await message.reply_text("❌I Need A Subtitle File")
                else:
                    await message.reply_text("❗Only Telegram File Is Supported")
            elif new_event=="stopped":
                break
            elif new_event=="cancelled":
                Cancel = True
                break
            elif not new_event:
                Cancel = True
                break
        if Cancel:
            del process_status
            return
        if len(process_status.subtitles)==0:
            del process_status
            await message.reply_text("❗Atleast 1 Files Required To SoftMux")
            return
        # REMOVED: get_thumbnail call
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        # REMOVED: Multi-task logic
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return

# REMOVED: Softremux handler

# MODIFIED: Use Pyrogram client and message
###############------Convert------###############
@PYROGRAM_CLIENT.on_message(filters.command("convert") & filters.private) # Use Pyrogram filters
async def _convert_video(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/convert", "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Convert video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.convert, custom_file_name) # Pass message
        # REMOVED: get_thumbnail call
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return


# MODIFIED: Use Pyrogram client and message
###############------hardmux------###############
@PYROGRAM_CLIENT.on_message(filters.command("hardmux") & filters.private) # Use Pyrogram filters
async def _hardmux_subtitle(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/hardmux", "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Hardmux video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.hardmux, custom_file_name) # Pass message
         # MODIFIED: Needs adaptation for Pyrogram
        # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/hardmux", "stop"], f"Send Subtitle SRT File", 120, False, True, allow_magnet=False, allow_url=False)
        await message.reply_text("Hardmux subtitle input needs adaptation for Pyrogram conversations.") # Placeholder
        new_event = None # Placeholder
        if new_event and new_event not in ["cancelled", "stopped"]:
            if new_event.document: # Check document
                # Mime type check might need adjustment
                # if not str(new_event.document.mime_type).startswith("video/") and not str(new_event.document.mime_type).startswith("image/"):
                if new_event.document.file_size < 512000: # Check size
                    sub_name = new_event.document.file_name
                    create_direc(f"{process_status.dir}/subtitles")
                    sub_dw_loc = check_file(f"{process_status.dir}/subtitles", sub_name)
                    sub_path = await client.download_media(new_event.document, file_name=sub_dw_loc) # Use client.download_media
                    process_status.append_subtitles(sub_path)
                else:
                    await message.reply_text("❌Subtitle Size Is More Than 500KB, Is This Really A Subtitle File")
                    del process_status
                    return
                # else:
                #     await message.reply_text("❌I Need A Subtitle File.")
                #     del process_status
                #     return
            else:
                await message.reply_text("❗Only Telegram File Is Supported")
                del process_status
                return
        else:
            # Handle cancellation or timeout if needed
            if new_event is None: # If placeholder was hit due to needing adaptation
                 await message.reply_text("Subtitle input cancelled due to pending Pyrogram adaptation.")
            del process_status
            return
        if len(process_status.subtitles)==0:
            del process_status
            await message.reply_text("❗Atleast 1 Files Required To hardmux")
            return
        # REMOVED: get_thumbnail call
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        # REMOVED: Multi-task logic
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return

# MODIFIED: Use Pyrogram client and message
###############------Change_Config------###############
@PYROGRAM_CLIENT.on_message(filters.command("changeconfig") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _changeconfig(client, message): # Use Pyrogram arguments
        if not exists('config.env'):
            await message.reply_text("❗`config.env` File Not Found")
            return
        tg_button = []
        for key in get_env_keys('config.env'):
            tg_button.append([InlineKeyboardButton(key, callback_data=f'env_{key}')]) # Use Pyrogram InlineKeyboardButton
        if tg_button:
            tg_button.append([InlineKeyboardButton('⭕Close Settings', callback_data='close_settings')])
            await message.reply_text("Choose Variable To Change", reply_markup=InlineKeyboardMarkup(tg_button)) # Use Pyrogram InlineKeyboardMarkup
        else:
            await message.reply_text("❗No Variable In `config.env` File")
        return

# MODIFIED: Use Pyrogram client and message
###############------Clear_Config------###############
@PYROGRAM_CLIENT.on_message(filters.command("clearconfigs") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _clearconfig(client, message): # Use Pyrogram arguments
        if exists('./userdata/botconfig.env'):
            remove("./userdata/botconfig.env")
            await message.reply_text(f"✅Successfully Cleared")
        else:
            await message.reply_text(f"❗Config Not Found")
        return

# MODIFIED: Use Pyrogram client and message
###############------Check_Sudo------###############
@PYROGRAM_CLIENT.on_message(filters.command("checksudo") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _checksudo(client, message): # Use Pyrogram arguments
    await message.reply_text(str(sudo_users))
    return


# MODIFIED: Use Pyrogram client and message
###############------Add_Sudo------###############
@PYROGRAM_CLIENT.on_message(filters.command("addsudo") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _addsudo(client, message): # Use Pyrogram arguments
    chat_id = message.chat.id
    user_id = message.from_user.id
    sudo_id = await get_sudo_user_id(message) # Pass Pyrogram message
    if not sudo_id:
         # MODIFIED: Needs adaptation for Pyrogram
        # sudo_id = await ask_text(client, chat_id, user_id, message, 120, "Send User ID", int)
        await message.reply_text("Sudo ID input needs adaptation for Pyrogram conversations.") # Placeholder
        sudo_id = None # Placeholder
        if not sudo_id:
            return
    if sudo_id not in sudo_users:
            sudo_users.append(sudo_id)
            if exists("./userdata/botconfig.env"):
                config_dict = get_env_dict('./userdata/botconfig.env')
            elif exists("config.env"):
                config_dict = get_env_dict('config.env')
            else:
                config_dict = {}
            sudo_data = ""
            for u in sudo_users:
                sudo_data+= f"{u} "
            config_dict["SUDO_USERS"] = sudo_data.strip()
            export_env_file("./userdata/botconfig.env", config_dict)
            await message.reply_text(f"✅Successfully Added To Sudo Users.\n\n{str(sudo_users)}")
            return
    else:
        await message.reply_text(f"❗ID Already In Sudo Users.\n\n{str(sudo_users)}")
        return


# MODIFIED: Use Pyrogram client and message
###############------Delete_Sudo------###############
@PYROGRAM_CLIENT.on_message(filters.command("delsudo") & filters.private & filters.user(owner_id)) # Use Pyrogram filters
async def _delsudo(client, message): # Use Pyrogram arguments
    chat_id = message.chat.id
    user_id = message.from_user.id
    sudo_id = await get_sudo_user_id(message) # Pass Pyrogram message
    if not sudo_id:
         # MODIFIED: Needs adaptation for Pyrogram
        # sudo_id = await ask_text(client, chat_id, user_id, message, 120, "Send User ID", int)
        await message.reply_text("Sudo ID input needs adaptation for Pyrogram conversations.") # Placeholder
        sudo_id = None # Placeholder
        if not sudo_id:
            return
    if sudo_id in sudo_users:
            sudo_users.remove(sudo_id)
            if exists("./userdata/botconfig.env"):
                config_dict = get_env_dict('./userdata/botconfig.env')
            elif exists("config.env"):
                config_dict = get_env_dict('config.env')
            else:
                config_dict = {}
            sudo_data = ""
            for u in sudo_users:
                sudo_data+= f"{u} "
            config_dict["SUDO_USERS"] = sudo_data.strip()
            export_env_file("./userdata/botconfig.env", config_dict)
            await message.reply_text(f"✅Successfully Removed From Sudo Users.\n\n{str(sudo_users)}")
            return
    else:
        await message.reply_text(f"❗ID Not Found In Sudo Users.\n\n{str(sudo_users)}")
        return


# MODIFIED: Use Pyrogram client and message
###############------Generate_Sample_Video------###############
@PYROGRAM_CLIENT.on_message(filters.command("gensample") & filters.private) # Use Pyrogram filters
async def _gen_video_sample(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/gensample", "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Sample video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.gensample, custom_file_name) # Pass message
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return

# MODIFIED: Use Pyrogram client and message
###############------Generate_Screenshots------###############
@PYROGRAM_CLIENT.on_message(filters.command("genss") & filters.private) # Use Pyrogram filters
async def _gen_screenshots(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, ["/genss", "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Screenshot video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.genss, custom_file_name) # Pass message
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return


# MODIFIED: Use Pyrogram client and message
###############------Change_MetaData------###############
@PYROGRAM_CLIENT.on_message(filters.command("changemetadata") & filters.private) # Use Pyrogram filters
async def _change_metadata(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        command = '/changemetadata'
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, [command, "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Metadata video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
         # MODIFIED: Needs adaptation for Pyrogram
        # metadata_event = await ask_text_event(client, chat_id, user_id, message, 120, "Send MetaData", message_hint="🔷`a` Is For Audio & `s` Is For Subtitle\n🔷 Send In The Format As Shown Below:\n\n`a:0-AudioLanguage-AudioTitle` (To Change Audio Number 1 Metadata)\n`s:0-SubLanguage-SubTitle` (To Change Subtitle Number 1 Metadata)\n\ne.g. `a:1-eng-nik66bots` (To Change Audio Number 2 Metadata)")
        await message.reply_text("Metadata text input needs adaptation for Pyrogram conversations.") # Placeholder
        metadata_event = None # Placeholder
        if not metadata_event:
            return
        custom_metadata_list = str(metadata_event.text).split('\n') # Use .text
        custom_metadata = []
        for m in custom_metadata_list:
            mdata = str(m).strip().split('-')
            LOGGER.info(mdata)
            try:
                sindex = str(mdata[0]).strip().lower()
                mlang =  str(mdata[1]).lower()
                mtilte = str(mdata[2])
                custom_metadata.append([f'-metadata:s:{sindex}', f"language={mlang}", f'-metadata:s:{str(sindex)}', f"title={mtilte}"])
            except Exception as e:
                await metadata_event.reply_text(f"❗Invalid Metadata, Error: {str(e)}") # Use reply_text
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.changeMetadata, custom_file_name, custom_metadata=custom_metadata) # Pass message
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        # REMOVED: get_thumbnail call
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return


# MODIFIED: Use Pyrogram client and message
###############------Change_index------###############
@PYROGRAM_CLIENT.on_message(filters.command("changeindex") & filters.private) # Use Pyrogram filters
async def _change_index(client, message): # Use Pyrogram arguments
        chat_id = message.chat.id
        user_id = message.from_user.id
        command = '/changeindex'
        if user_id not in get_data():
                await new_user(user_id, SAVE_TO_DATABASE)
        link, custom_file_name = await get_link(client, message) # Pass client and message
        if link=="invalid":
            await message.reply_text("❗Invalid link")
            return
        elif not link:
             # MODIFIED: Needs adaptation for Pyrogram
            # new_event = await ask_media_OR_url(client, message, chat_id, user_id, [command, "stop"], "Send Video or URL", 120, "video/", True)
            await message.reply_text("Index video input needs adaptation for Pyrogram conversations.") # Placeholder
            new_event = None # Placeholder
            if new_event and new_event not in ["cancelled", "stopped"]:
                link = await get_url_from_message(new_event) # Pass Pyrogram message
            else:
                return
         # MODIFIED: Needs adaptation for Pyrogram
        # index_event = await ask_text_event(client, chat_id, user_id, message, 120, "Send index", message_hint="🔷`a` Is For Audio & `s` Is For Subtitle\n🔷 Send In The Format As Shown Below:\n\n`a-3-1-2` (To Change Audio Index In 3rd, 1st and 2nd order)\n`s-2-1` (To Change Subtitle Index In 2nd and 1st order)")
        await message.reply_text("Index text input needs adaptation for Pyrogram conversations.") # Placeholder
        index_event = None # Placeholder
        if not index_event:
            return
        custom_index_list = str(index_event.text).split('\n') # Use .text
        custom_index = []
        for m in custom_index_list:
            mdata = str(m).strip().split('-')
            LOGGER.info(mdata)
            try:
                stream = str(mdata[0]).strip().lower()
                mdata.pop(0)
                for s in mdata:
                    s = int(s.strip())-1
                    custom_index.append("-map")
                    custom_index.append(f"0:{stream}:{s}")
                custom_index+= [f"-disposition:{stream}:0", "default"]
            except Exception as e:
                await index_event.reply_text(f"❗Invalid index, Error: {str(e)}") # Use reply_text
                return
        user_name = get_username(message)
        user_first_name = message.from_user.first_name
        process_status = ProcessStatus(user_id, chat_id, user_name, user_first_name, message, Names.changeindex, custom_file_name, custom_index=custom_index) # Pass message
        task = {}
        task['process_status'] = process_status
        task['functions'] = []
        if type(link)==str:
                task['functions'].append(["Aria", Aria2.add_aria2c_download, [link, process_status, False, False, False, False]])
        else:
            task['functions'].append(["TG", [link]]) # Pass Pyrogram message object
        # REMOVED: get_thumbnail call
        create_task(add_task(task))
        await update_status_message(client, message) # Pass client and message
        return


# REMOVED: Leech handler
# ###############------Leech_File------###############
# @TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/leech', func=lambda e: user_auth_checker(e)))
# async def _leech_file(event):
#         ... (function content removed) ...


# REMOVED: Mirror handler
# ###############------mirror_File------###############
# @TELETHON_CLIENT.on(events.NewMessage(incoming=True, pattern='/mirror', func=lambda e: user_auth_checker(e)))
# async def _mirror_file(event):
#         ... (function content removed) ...

# --- END OF FILE VideoFlux-Re-master/bot/start.py ---
