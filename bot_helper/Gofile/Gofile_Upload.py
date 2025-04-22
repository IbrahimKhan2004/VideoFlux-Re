# --- START OF FILE VideoFlux-Re-master/bot_helper/Gofile/Gofile_Upload.py ---

import aiohttp
import aiofiles
import os
from bot_helper.Others.Names import Names
from bot_helper.Database.User_Data import get_data # Import get_data if needed for Gofile specific settings later
from bot_helper.Process.Running_Process import check_running_process
from config.config import LOGGER
from bot_helper.Others.Helper_Functions import get_human_size
from time import time
# Highlighted change: Import ClientTimeout
from aiohttp import ClientTimeout
# End of highlighted change

# Gofile API endpoint
GOFILE_UPLOAD_API = "https://upload.gofile.io/uploadfile"
# Highlighted change: Define a longer timeout (e.g., 30 minutes = 1800 seconds)
# None means infinite timeout, but setting a large value is often safer.
# Adjust this value based on expected upload times.
UPLOAD_TIMEOUT_SECONDS = 1800
# End of highlighted change


async def upload_gofile(process_status):
    """
    Uploads files listed in process_status.send_files to Gofile.
    """
    total_files = len(process_status.send_files)
    files_to_upload = process_status.send_files
    user_id = process_status.user_id
    chat_id = process_status.chat_id
    event = process_status.event
    process_id = process_status.process_id
    caption = process_status.caption if process_status.caption else ""

    LOGGER.info(f"Starting Gofile upload for process {process_id}. Total files: {total_files}")

    # Highlighted change: Set timeout for the session
    timeout = ClientTimeout(total=UPLOAD_TIMEOUT_SECONDS)
    async with aiohttp.ClientSession(timeout=timeout) as session:
    # End of highlighted change
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
            LOGGER.info(f"Uploading {filename} to Gofile...")
            start_time = time()

            try:
                # Prepare multipart data
                data = aiohttp.FormData()
                # Use aiofiles for async file reading
                # Highlighted change: Stream the file instead of reading all at once
                async with aiofiles.open(file_path, 'rb') as f:
                    # Pass the file object directly to add_field for streaming
                    data.add_field('file',
                                   f, # Pass the async file handle
                                   filename=filename,
                                   content_type='application/octet-stream') # Or detect mime type

                    # Make the POST request *inside* the file open block
                    # This ensures the file is open while aiohttp streams it
                    async with session.post(GOFILE_UPLOAD_API, data=data) as response:
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
                                        f"✅ Successfully Uploaded `{filename}` to Gofile\n\n"
                                        f"🔗 Link: {download_page}\n"
                                        f"💽 Size: {file_size_str}\n"
                                        f"⏱ Time: {int(upload_duration)}s\n\n"
                                        f"{caption}"
                                    )
                                    await event.reply(success_message)
                                    LOGGER.info(f"Successfully uploaded {filename} to Gofile: {download_page}")
                                else:
                                    error_detail = response_data.get("status", "Unknown error")
                                    await event.reply(f"❌ Gofile upload failed for `{filename}`. Reason: {error_detail}")
                                    LOGGER.error(f"Gofile API returned error for {filename}: {error_detail} | Response: {response_text}")
                            except Exception as json_e: # Catch JSON decoding errors
                                await event.reply(f"❌ Failed to parse Gofile response for `{filename}`. Status: {response.status}. Response: ```{response_text[:1000]}...```")
                                LOGGER.error(f"Failed to parse Gofile JSON response for {filename}: {json_e} | Status: {response.status} | Response: {response_text}")
                        else:
                            await event.reply(f"❌ Gofile upload failed for `{filename}`. HTTP Status: {response.status}. Response: ```{response_text[:1000]}...```")
                            LOGGER.error(f"Gofile upload HTTP error for {filename}: Status {response.status} | Response: {response_text}")
                # End of highlighted change

            except aiohttp.ClientError as e:
                # Highlighted change: Check if the error is specifically a timeout error
                if isinstance(e, asyncio.TimeoutError):
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
                    LOGGER.exception(f"Unexpected error during Gofile upload for {filename}:") # Log full traceback

    LOGGER.info(f"Gofile upload process finished for {process_id}")

# --- END OF FILE VideoFlux-Re-master/bot_helper/Gofile/Gofile_Upload.py ---
