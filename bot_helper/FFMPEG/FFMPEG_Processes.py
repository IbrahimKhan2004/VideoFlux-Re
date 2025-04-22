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
    ###############------Change_Metadata------###############
    async def change_metadata(process_status):
        if get_data()[process_status.user_id]['custom_metadata']:
                dl_loc = f'{str(process_status.send_files[-1])}'
                direc = f"{process_status.dir}/metadata/"
                create_direc(direc)
                output_meta = f"{direc}/{get_output_name(process_status)}"
                custom_metadata_title = get_data()[process_status.user_id]['metadata']
                process_status.update_process_message(f"🪀Changing MetaData\n{process_status.get_task_details()}")
                # Updated command structure based on VFBITMOD-update
                cmd_meta = ["ffmpeg", "-i", f"{dl_loc}", # Reverted zender -> ffmpeg
                            "-metadata", f"title={custom_metadata_title}",
                            "-metadata:s:v", f"title={custom_metadata_title}",
                            "-metadata:s:v", f"channel={custom_metadata_title}", # Added channel metadata
                            "-metadata:s:a", f"title={custom_metadata_title}",
                            "-metadata:s:s", f"title={custom_metadata_title}",
                            "-map", "0", "-c", "copy", '-y', f"{output_meta}"]
                met_result = await run_process_command(cmd_meta)
                # Removed fallback commands as the primary one now includes all necessary flags
                if met_result:
                        await process_status.event.reply(f"✅Metadata Set Successfully")
                        # Corrected caption logic
                        caption = f"✅Metadata: {custom_metadata_title}\n" + (process_status.caption if process_status.caption else '')
                        process_status.set_caption(caption)
                        process_status.append_send_files_loc(output_meta)
                        return
                else:
                        await process_status.event.reply(f"❗Failed To Set MetaData")
                        return
        else:
            return

    # REMOVED: select_audio function
    # ###############------Select_Audio------###############
    # async def select_audio(process_status):
    #                                     ... (function content removed) ...

# --- END OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Processes.py ---
