# --- START OF FILE VideoFlux-Re-master/bot_helper/Telegram/Telegram_Client.py ---

from config.config import Config
# REMOVED: Telethon imports
# from telethon import TelegramClient
# from telethon.sessions import StringSession
from pyrogram import Client as PyrogramClient
from bot_helper.Others.Helper_Functions import get_video_duration
# REMOVED: Fast_Telethon import
# from bot_helper.Telegram.Fast_Telethon import upload_file, download_file
from bot_helper.Database.User_Data import get_data
from time import time
# REMOVED: Telethon types import
# from telethon.tl.types import DocumentAttributeVideo
from bot_helper.Process.Running_Process import check_running_process
from bot_helper.Others.Names import Names
from os.path import isdir, getsize
from os import makedirs
# REMOVED: FFMPEG import (already removed in previous step)
# from bot_helper.FFMPEG.FFMPEG_Processes import FFMPEG
from bot_helper.Rclone.Rclone_Upload import upload_single_drive
from os.path import exists
from bot_helper.Others.Helper_Functions import verify_rclone_account
# ADDED: Pyrogram types import (might be needed for attributes later, though not used currently)
from pyrogram.types import DocumentAttributeVideo


def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return

async def check_size_limit():
        # MODIFIED: Simplified - always return 2GB as Telethon user check is removed
        size = 2097151000
        # if Telegram.TELETHON_USER_CLIENT:
        #         user = await Telegram.TELETHON_USER_CLIENT.get_me()
        #         if user.premium:
        #             size = 4194304000
        return size

# REMOVED: get_split_size function (already removed in previous step)


LOGGER = Config.LOGGER


class Telegram:
    # REMOVED: Telethon client initialization
    # TELETHON_CLIENT = TelegramClient(Config.NAME, Config.API_ID, Config.API_HASH)
    PYROGRAM_CLIENT = PyrogramClient(
    f"Pyrogram_{Config.NAME}",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TOKEN)
    # REMOVED: Telethon user client initialization
    # if Config.USE_SESSION_STRING=="True":
    #     TELETHON_USER_CLIENT = TelegramClient(StringSession(Config.SESSION_STRING), Config.API_ID, Config.API_HASH)
    # else:
    #     TELETHON_USER_CLIENT = False
    TELETHON_USER_CLIENT = None # MODIFIED: Set to None explicitly

    async def upload_videos_on_telegram(process_status):
            total_files = len(process_status.send_files)
            files = process_status.send_files
            chat_id = process_status.chat_id
            caption = process_status.caption
            event = process_status.event
            process_id = process_status.process_id
            thumbnail = process_status.thumbnail if process_status.thumbnail else "./thumb.jpg"
            for i in range(total_files):
                start_time = time()
                duration = get_video_duration(files[i])
                filename = files[i].split("/")[-1]
                file_caption = f"**Name**: {filename}\n" + str(caption).strip() if caption else f"**Name**: {filename}"
                status = f"{Names.STATUS_UPLOADING} [{str(i+1)}/{str(total_files)}]"
                size_limit = await check_size_limit() # Will now always be 2GB
                file_size = getsize(files[i])

                if file_size > size_limit: # Check against the 2GB limit
                        r_config = f'./userdata/{str(process_status.user_id)}_rclone.conf'
                        drive_name = get_data()[process_status.user_id]['drive_name']
                        if get_data()[process_status.user_id]['auto_drive'] and exists(r_config) and verify_rclone_account(r_config, drive_name):
                                await upload_single_drive(process_status, files[i], status, r_config, drive_name, filename)
                        else:
                            # MODIFIED: Simplified error message as 4GB upload is removed
                            await event.reply(f"❌File Size ({get_human_size(file_size)}) Is Greater Than Telegram Upload Limit ({get_human_size(size_limit)})")
                            LOGGER.info(f"File Size: {file_size}, Limit: {size_limit}, Name: {filename}")
                else: # file_size <= 2097151000
                        # REMOVED: Telethon upload block
                        # if get_data()[process_status.user_id]['tgupload']=="Telethon":
                        #         ... (Telethon upload logic removed) ...
                        # else: # Defaulting to Pyrogram
                        if process_status.event.is_group and Config.AUTH_GROUP_ID:
                                    chat_id = Config.AUTH_GROUP_ID
                        try:
                                uploaded_file = await Telegram.PYROGRAM_CLIENT.send_video(
                                                                            chat_id=chat_id,
                                                                            file_name=filename,
                                                                            video=files[i],
                                                                            caption=file_caption,
                                                                            supports_streaming=True,
                                                                            duration=duration,
                                                                            thumb=thumbnail,
                                                                            reply_to_message_id=event.message.id,
                                                                            progress=process_status.telegram_update_status,
                                                                            # MODIFIED: Removed engine argument
                                                                            progress_args=("Uploaded", filename, start_time, status, Telegram.PYROGRAM_CLIENT))
                        except Exception as e:
                                await event.reply(f"❗Pyrogram Upload Error: {str(e)}")

                # REMOVED: Telethon User Client upload block (for >2GB)
                # else:
                #     if Telegram.TELETHON_USER_CLIENT:
                #             ... (Telethon user upload logic removed) ...
                #     else:
                #             await event.reply(f"❌File Size Is Greater Than Telegram Upload Limit")
                #             LOGGER.info(f"File Size: {file_size}, Name: {filename}")

                if not check_running_process(process_id):
                        await event.reply("🔒Task Cancelled By User")
                        break
            return

    async def download_tg_file(process_status, variables, dw_index):
        start_time = time()
        status = f"{Names.STATUS_DOWNLOADING} [{dw_index}]"
        new_event = variables[0]
        try:
            # MODIFIED: Use Pyrogram message structure directly
            message_obj = await Telegram.PYROGRAM_CLIENT.get_messages(process_status.chat_id, new_event.id)
            if message_obj.video:
                file_name = message_obj.video.file_name
                file_id = message_obj.video.file_id # Use file_id for Pyrogram download
            elif message_obj.document:
                file_name = message_obj.document.file_name
                file_id = message_obj.document.file_id # Use file_id for Pyrogram download
            else:
                 # Fallback if it's neither video nor document (might need adjustment)
                 file_name = f"unknown_file_{new_event.id}"
                 file_id = new_event.id # Use message id as fallback file_id
            if not file_name: # Handle cases where filename might be None
                ext = message_obj.document.mime_type.split('/')[-1] if message_obj.document else 'bin'
                file_name = f"download_{file_id}.{ext}"

        except Exception as e:
             LOGGER.error(f"Error getting file details from Pyrogram message: {e}")
             await process_status.event.reply("❗Could not get file details for download.")
             return False

        create_direc(process_status.dir)
        download_location = f"{process_status.dir}/{file_name}"
        process_status.append_dw_files(file_name)

        # REMOVED: Telethon download block
        # if get_data()[process_status.user_id]['tgdownload']=="Telethon":
        #         ... (Telethon download logic removed) ...
        # else: # Defaulting to Pyrogram
        try:
                if process_status.event.is_group and Config.AUTH_GROUP_ID:
                        chat_id = Config.AUTH_GROUP_ID
                else:
                        chat_id = process_status.chat_id
                await Telegram.PYROGRAM_CLIENT.download_media(
                                                            # MODIFIED: Pass file_id directly
                                                            message=file_id,
                                                            file_name=download_location,
                                                            progress=process_status.telegram_update_status,
                                                            # MODIFIED: Removed engine argument
                                                            progress_args=("Downloaded", file_name, start_time, status, Telegram.PYROGRAM_CLIENT))
                if not check_running_process(process_status.process_id):
                                await new_event.reply("🔒Task Cancelled By User")
                                return False # Added return False on cancellation
        except Exception as e:
                await process_status.event.reply(f"❗Pyrogram Download Error: {str(e)}\n\nChat: {chat_id}") # MODIFIED: Used process_status.event
                return False
        process_status.move_dw_file(file_name)
        return True

    async def upload_videos(process_status):
        # REMOVED: Splitting logic (already removed in previous step)
        await Telegram.upload_videos_on_telegram(process_status)

# --- END OF FILE VideoFlux-Re-master/bot_helper/Telegram/Telegram_Client.py ---
