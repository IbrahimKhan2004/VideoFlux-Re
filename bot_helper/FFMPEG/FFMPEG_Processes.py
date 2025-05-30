# --- START OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Processes.py ---

from bot_helper.Database.User_Data import get_data
from json import loads
from bot_helper.Others.Helper_Functions import execute, get_video_duration, get_readable_time, delete_trash
from config.config import Config
from asyncio import create_subprocess_exec, sleep
from asyncio.subprocess import PIPE as asyncioPIPE
from os.path import isdir, exists, getsize, splitext, join
from os import makedirs, remove
from telethon.tl.types import DocumentAttributeVideo
from time import time
from math import ceil


def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return

def get_output_name(process_status):
    if process_status.file_name:
        return process_status.file_name
    else:
        return process_status.send_files[-1].split("/")[-1]


LOGGER = Config.LOGGER


###############------Run_Command------###############
async def run_process_command(command):
    print(command)
    try:
        process = await create_subprocess_exec(
            *command,
            stdout=asyncioPIPE,
            stderr=asyncioPIPE,
            )
        while True:
                    try:
                            async for line in process.stderr:
                                        line = line.decode('utf-8').strip()
                                        print(line)
                    except ValueError:
                            continue
                    else:
                            break
        await process.wait()
        return_code = process.returncode
        if return_code == 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


###############------Get_Sample_Video_Cut_Duration------###############
async def get_cut_duration(duration):
    if duration<60:
                return [1, duration-2]
    else:
        vmid = round(duration/2)-2
        vend = vmid+60
        if vend>duration:
            vend = duration-2
        return [vmid, vend]


###############------Get_ScreenShot_List------###############
async def gen_ss_list(duration, ss_no):
    value = round(duration/ss_no)
    ss_list = [5]
    ss = 5
    while True:
        ss = ss+value
        if len(ss_list)==ss_no:
            break
        if ss<duration:
            ss_list.append(ss)
        else:
            ss_list.append(duration-2)
            break
    return ss_list

###############------Generate_ScreenShot------###############
async def generate_screenshoot(ss_time, input_video, ss_name):
    command = [
        "ffmpeg", # Reverted zender -> ffmpeg
        "-ss",
        str(ss_time),
        "-i",
        input_video,
        "-frames:v",
        "1",
        "-f",
        "image2",
        "-map",
        "0:v:0",
        "-y",
        ss_name
    ]
    return await run_process_command(command)


class FFMPEG:

    # REMOVED: split_video_file function
    # ###############------Split_Video------###############
    # async def split_video_file(file, split_size, dirpath, event):
    #     ... (function content removed) ...

###############------Send_ScreenShots------###############
    async def generate_ss(process_status, force_gen=False):
                if get_data()[process_status.user_id]['gen_ss'] or force_gen:
                        if not force_gen:
                                ss_n0 = get_data()[process_status.user_id]['ss_no']
                        else:
                                ss_n0 = 9
                        file_name = get_output_name(process_status)
                        process_status.update_process_message(f"📷Generating Screenshots\n`{str(file_name)}`\n{process_status.get_task_details()}")
                        input_video = f'{str(process_status.send_files[-1])}'
                        duration = get_video_duration(input_video)
                        ss_list = await gen_ss_list(duration, ss_n0)
                        sn0 = 1
                        for ss_time in ss_list:
                                ss_name = f"{process_status.dir}/screenshot_{str(time())}.jpg"
                                ssresult = await generate_screenshoot(ss_time, input_video, ss_name)
                                if ssresult and exists(ss_name):
                                        sscaption = f"📌 Position: {str(get_readable_time(ss_time))}\n📷 Screenshot: {str(sn0)}/{str(ss_n0)}"
                                        try:
                                                await process_status.event.client.send_file(process_status.chat_id, file=ss_name, allow_cache=False, reply_to=process_status.event.message, caption=sscaption)
                                        except Exception as e:
                                                LOGGER.info(str(e))
                                        remove(ss_name)
                                        sn0+=1
                                        await sleep(1)
                return

###############------Send_Sample_Video------###############
    async def gen_sample_video(process_status, force_gen=False):
        if get_data()[process_status.user_id]['gen_sample'] or force_gen:
                input_video = f'{str(process_status.send_files[-1])}'
                duration = get_video_duration(input_video)
                if duration>60:
                        file_name = get_output_name(process_status)
                        process_status.update_process_message(f"🎞Generating Sample Video\n`{str(file_name)}`\n{process_status.get_task_details()}")
                        sample_name = f"{process_status.dir}/sample_{file_name}"
                        vstart_time, vend_time = await get_cut_duration(duration)
                        if duration<180:
                                vframes = '750'
                        else:
                                vframes = '1500'
                        # cmd_sample = ["ffmpeg", "-ss", str(vstart_time), "-to",  str(vend_time), "-i", f"{input_video}","-c", "copy", '-y', f"{sample_name}"] # Old command
                        cmd_sample= ['ffmpeg', '-ss', f'{vstart_time}s', '-i', f"{input_video}", '-vframes', f'{vframes}', '-vsync', '1', '-async', '-1', '-acodec', 'copy', '-vcodec', 'copy', '-y', f"{sample_name}"] # Reverted zender -> ffmpeg
                        sample_result = await run_process_command(cmd_sample)
                        if sample_result and exists(sample_name):
                                try:
                                        await process_status.event.client.send_file(process_status.chat_id, file=sample_name, allow_cache=False, reply_to=process_status.event.message, caption=f"🎞 Sample Video", thumb="sthumb.jpg", supports_streaming=True, attributes=(DocumentAttributeVideo(get_video_duration(sample_name), 0, 0),))
                                except Exception as e:
                                        LOGGER.info(str(e))
                                remove(sample_name)
                        else:
                                await process_status.event.reply(f'❌Failed To Generate Sample Video')
                else:
                        if force_gen:
                                await process_status.event.reply(f'❌Video Duration Must Be Greater Than 60 secs To Generate Sample')
        return
# START OF MODIFIED BLOCK
    ###############------Change_Metadata------###############
    async def change_metadata(process_status):
        if get_data()[process_status.user_id]['custom_metadata']:
                dl_loc = f'{str(process_status.send_files[-1])}'
                direc = f"{process_status.dir}/metadata_final/" # Changed temp directory name slightly
                create_direc(direc)
                # Create a new output file name to signify it's the metadata-applied version
                base_output_name, ext = splitext(get_output_name(process_status))
                output_meta = f"{direc}/{base_output_name}_meta{ext if ext else '.mkv'}"

                user_metadata_text = get_data()[process_status.user_id]['metadata'] # This is the user's text
                
                process_status.update_process_message(f"🪀Applying Enhanced MetaData\n{process_status.get_task_details()}")
                
                cmd_meta = ["ffmpeg", "-i", f"{dl_loc}"]

                if user_metadata_text and user_metadata_text.strip(): # Check if user text is not empty
                    LOGGER.info(f"Applying user metadata text: '{user_metadata_text}' to standard fields and stream titles.")
                    cmd_meta.extend(['-metadata', f'title={user_metadata_text}'])
                    cmd_meta.extend(['-metadata', f'author={user_metadata_text}'])
                    cmd_meta.extend(['-metadata', f'comment={user_metadata_text}'])
                    # Stream specific titles using user's text
                    cmd_meta.extend(['-metadata:s:v:0', f'title={user_metadata_text}']) # For the first video stream
                    cmd_meta.extend(['-metadata:s:a', f'title={user_metadata_text}'])   # For all audio streams
                    cmd_meta.extend(['-metadata:s:s', f'title={user_metadata_text}'])   # For all subtitle streams (will apply if -map 0 -c copy is used and subs exist)
                else:
                    LOGGER.info("User metadata text is empty or not set, skipping user-specific title/author/comment/stream titles.")

                # Fixed metadata fields (applied if 'custom_metadata' toggle is True)
                cmd_meta.extend(['-metadata', 'encoded_by=BashAFK'])
                cmd_meta.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
                cmd_meta.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
                LOGGER.info("Applied fixed metadata: encoded_by, description, telegram tags.")
                
                # Ensure all streams are mapped and codecs are copied
                cmd_meta.extend(["-map", "0", "-c", "copy", '-y', f"{output_meta}"])
                
                met_result = await run_process_command(cmd_meta)
                
                if met_result and exists(output_meta): # Check if output file was created
                        await process_status.event.reply(f"✅Metadata Applied Successfully")
                        # Update caption and process_status to use the new metadata-applied file
                        new_caption_text = user_metadata_text if user_metadata_text and user_metadata_text.strip() else "Default"
                        caption = f"✅Metadata: {new_caption_text}\n" + (process_status.caption if process_status.caption else '')
                        process_status.set_caption(caption)
                        # Replace the old file in send_files with the new metadata-applied one
                        if dl_loc in process_status.send_files:
                            process_status.send_files.remove(dl_loc)
                        process_status.append_send_files_loc(output_meta)
                        # Optionally, delete the original dl_loc if it's a temporary file from a previous step
                        # For now, let's assume it might be needed or will be cleaned up by the main task clearer
                        return True # Indicate success
                else:
                        await process_status.event.reply(f"❗Failed To Apply MetaData")
                        return False # Indicate failure
        else: # If custom_metadata is False in user settings
            return True # Indicate success (as in, no metadata operation was requested or failed)
# END OF MODIFIED BLOCK

    # REMOVED: select_audio function
    # ###############------Select_Audio------###############
    # async def select_audio(process_status):
    #                                     ... (function content removed) ...

# --- END OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Processes.py ---
