import aiohttp
import aiofiles
import os
from bot_helper.Others.Names import Names
# Removed User_Data import as token is hardcoded
from bot_helper.Process.Running_Process import check_running_process
from config.config import LOGGER
from bot_helper.Others.Helper_Functions import get_human_size
from time import time
# Highlighted change: Import ClientTimeout
from aiohttp import ClientTimeout
# Highlighted change: Import Union for older Python compatibility
from typing import Union
# Highlighted change: Removed Lock import as root folder ID caching is removed
# from asyncio import Lock # Import Lock for thread safety if needed for root folder ID caching

# --- Gofile API Configuration ---
# Highlighted change: GOFILE_API_TOKEN is no longer used for anonymous upload
# GOFILE_API_TOKEN = "lBZPR77YTHyquQPpDlCoMbiYWh8B0mbK" # Hardcoded API Token
GOFILE_API_BASE = "https://api.gofile.io/servers"
" # Still needed for server list if not using upload.gofile.io
# Gofile API endpoint - Using the main upload endpoint which handles anonymous uploads
GOFILE_UPLOAD_API = "https://upload.gofile.io/uploadfile"
# --- End Gofile API Configuration ---

# Highlighted change: Define a longer timeout (e.g., 30 minutes = 1800 seconds)
# None means infinite timeout, but setting a large value is often safer.
# Adjust this value based on expected upload times.
UPLOAD_TIMEOUT_SECONDS = 1800
# End of highlighted change

# --- Root Folder ID Caching ---
# Highlighted change: Removed root folder ID caching as it's not used for anonymous uploads
# root_folder_id_cache = None
# root_folder_id_lock = Lock()
# --- End Root Folder ID Caching ---

# Highlighted change: Removed get_gofile_root_folder_id function as it's not needed for anonymous uploads
# async def get_gofile_root_folder_id(session: aiohttp.ClientSession) -> Union[str, None]:
#     """Fetches the Gofile account's root folder ID using the API token."""
#     global root_folder_id_cache
#     async with root_folder_id_lock:
#         if root_folder_id_cache:
#             return root_folder_id_cache

#         if not GOFILE_API_TOKEN:
#             LOGGER.error("Gofile API Token is not set.")
#             return None

#         headers = {"Authorization": f"Bearer {GOFILE_API_TOKEN}"}
#         account_id = None

#         # 1. Get Account ID
#         try:
#             get_id_url = f"{GOFILE_API_BASE}/accounts/getid"
#             async with session.get(get_id_url, headers=headers) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     if data.get("status") == "ok":
#                         account_id = data.get("data", {}).get("id")
#                         LOGGER.info(f"Gofile Account ID fetched: {account_id}")
#                     else:
#                         LOGGER.error(f"Failed to get Gofile Account ID: {data.get('status', 'Unknown error')}")
#                         return None
#                 else:
#                     LOGGER.error(f"Failed to get Gofile Account ID. HTTP Status: {response.status}, Response: {await response.text()}")
#                     return None
#         except Exception as e:
#             LOGGER.error(f"Error fetching Gofile Account ID: {e}")
#             return None

#         if not account_id:
#             return None

#         # 2. Get Account Details (including root folder ID)
#         try:
#             get_account_url = f"{GOFILE_API_BASE}/accounts/{account_id}"
#             async with session.get(get_account_url, headers=headers) as response:
#                 if response.status == 200:
#                     data = await response.json()
#                     if data.get("status") == "ok":
#                         root_folder_id = data.get("data", {}).get("rootFolder")
#                         if root_folder_id:
#                             LOGGER.info(f"Gofile Root Folder ID fetched: {root_folder_id}")
#                             root_folder_id_cache = root_folder_id # Cache the ID
#                             return root_folder_id
#                         else:
#                             LOGGER.error("Root Folder ID not found in Gofile account details.")
#                             return None
#                     else:
#                         LOGGER.error(f"Failed to get Gofile Account Details: {data.get('status', 'Unknown error')}")
#                         return None
#                 else:
#                     LOGGER.error(f"Failed to get Gofile Account Details. HTTP Status: {response.status}, Response: {await response.text()}")
#                     return None
#         except Exception as e:
#             LOGGER.error(f"Error fetching Gofile Account Details: {e}")
#             return None


async def upload_gofile(process_status):
    """
    Uploads files listed in process_status.send_files to Gofile anonymously.
    """
    total_files = len(process_status.send_files)
    files_to_upload = process_status.send_files
    # user_id = process_status.user_id # Not needed
    chat_id = process_status.chat_id
    event = process_status.event
    process_id = process_status.process_id
    caption = process_status.caption if process_status.caption else ""

    # Highlighted change: Removed API token check as it's not used for anonymous upload
    # if not GOFILE_API_TOKEN:
    #     await event.reply("❌ Gofile API Token is not configured. Cannot upload.")
    #     LOGGER.error("Gofile upload skipped: API Token not configured.")
    #     return

    LOGGER.info(f"Starting Gofile anonymous upload for process {process_id}. Total files: {total_files}")

    # Highlighted change: Set timeout for the session
    timeout = ClientTimeout(total=UPLOAD_TIMEOUT_SECONDS)
    async with aiohttp.ClientSession(timeout=timeout) as session:
    # End of highlighted change
        # Highlighted change: Removed fetching root folder ID as it's not needed for anonymous uploads
        # root_folder_id = await get_gofile_root_folder_id(session)
        # if not root_folder_id:
        #     await event.reply("❌ Failed to get Gofile Root Folder ID. Cannot upload.")
        #     return

        for i, file_path in enumerate(files_to_upload):
            if not check_running_process(process_id):
                await event.reply("🔒 Task Cancelled By User (during Gofile upload).")
                LOGGER.info(f"Gofile upload cancelled by user for process {process_id}")
                return

            if not os.path.exists(file_path):
                LOGGER.error(f"File not found for Gofile upload: {file_path}")
                await event.reply(f"❌ File not found, skipping Gofile upload: `{os.path.basename(file_path)}`")
                continue

            filename = os.path.basename(file_path)
            status_msg = f"{Names.STATUS_UPLOADING} to Gofile [{str(i+1)}/{str(total_files)}]"
            process_status.update_process_message(f"{status_msg}\n`{filename}`\n{process_status.get_task_details()}")
            LOGGER.info(f"Uploading {filename} to Gofile anonymously...")
            start_time = time()

            try:
                # Prepare multipart data
                data = aiohttp.FormData()
                # Highlighted change: Removed folderId parameter as it's not used for anonymous uploads
                # data.add_field('folderId', root_folder_id)

                # Use aiofiles for asynchronous file handling
                # Keep the file open within the session.post context
                async with aiofiles.open(file_path, 'rb') as f:
                    data.add_field('file',
                                   f,  # Pass the async file handle
                                   filename=filename,
                                   content_type='application/octet-stream')

                    # Make the POST request (file is already in FormData)
                    # Highlighted change: Removed Authorization header as it's not needed for anonymous uploads
                    async with session.post(
                        GOFILE_UPLOAD_API,
                        data=data,
                        # headers={"Authorization": f"Bearer {GOFILE_API_TOKEN}"} # Removed header
                    ) as response:
                        upload_duration = time() - start_time
                        response_text = await response.text()
                        LOGGER.debug(f"Gofile API response status: {response.status}")
                        LOGGER.debug(f"Gofile API response body: {response_text}")

                        if response.status == 200:
                            try:
                                response_data = await response.json()
                                if response_data.get("status") == "ok":
                                    download_page = response_data.get("data", {}).get("downloadPage", "N/A")
                                    file_size_str = get_human_size(os.path.getsize(file_path))
                                    success_message = (
                                        f"✅ Successfully Uploaded `{filename}` to Gofile (Anonymous)\n\n" # Added (Anonymous)
                                        f"🔗 Link: {download_page}\n"
                                        f"💽 Size: {file_size_str}\n"
                                        f"⏱ Time: {int(upload_duration)}s\n\n"
                                        f"{caption}"
                                    )
                                    await event.reply(success_message)
                                    LOGGER.info(f"Successfully uploaded {filename} to Gofile anonymously: {download_page}")
                                else:
                                    error_detail = response_data.get("status", "Unknown error")
                                    await event.reply(f"❌ Gofile upload failed for `{filename}`. Reason: {error_detail}")
                                    LOGGER.error(f"Gofile API returned error for {filename}: {error_detail} | Response: {response_text}")
                            except Exception as json_e:  # Catch JSON decoding errors
                                await event.reply(
                                    f"❌ Failed to parse Gofile response for `{filename}`. Status: {response.status}. Response: ```{response_text[:1000]}...```"
                                )
                                LOGGER.error(f"Failed to parse Gofile JSON response for {filename}: {json_e} | Status: {response.status} | Response: {response_text}")
                        else:
                            await event.reply(
                                f"❌ Gofile upload failed for `{filename}`. HTTP Status: {response.status}. Response: ```{response_text[:1000]}...```"
                            )
                            LOGGER.error(f"Gofile upload HTTP error for {filename}: Status {response.status} | Response: {response_text}")

            except aiohttp.ClientError as e:
                # Highlighted change: Check if the error is specifically a timeout error
                # Check for timeout explicitly (ClientTimeoutError is raised in newer aiohttp)
                if isinstance(e, aiohttp.ClientTimeoutError) or isinstance(e, TimeoutError):  # Add TimeoutError for broader compatibility
                    await event.reply(f"❌ Gofile upload timed out for `{filename}` after {UPLOAD_TIMEOUT_SECONDS}s. Server might be slow or network unstable.")
                    LOGGER.error(f"Gofile upload timed out for {filename}.")
                else:
                    await event.reply(f"❌ Network error during Gofile upload for `{filename}`: {e}")
                    LOGGER.error(f"Network error during Gofile upload for {filename}: {e}")
                # End of highlighted change
            except Exception as e:
                # Catch MemoryError specifically if it still occurs somehow
                if isinstance(e, MemoryError):
                    await event.reply(f"❌ Ran out of memory during Gofile upload for `{filename}`. File might be too large for available resources.")
                    LOGGER.error(f"MemoryError during Gofile upload for {filename}. File size: {get_human_size(os.path.getsize(file_path))}")
                else:
                    await event.reply(f"❌ An unexpected error occurred during Gofile upload for `{filename}`: {e}")
                    LOGGER.exception(f"Unexpected error during Gofile upload for {filename}:")  # Log full traceback

    LOGGER.info(f"Gofile anonymous upload process finished for {process_id}")
