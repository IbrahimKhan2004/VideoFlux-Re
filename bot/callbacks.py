# --- START OF FILE VideoFlux-Re-master/bot/callbacks.py ---

from telethon import events
from telethon.tl.custom import Button
from config.config import Config
from bot_helper.Others.Helper_Functions import delete_all, get_config, get_env_dict, export_env_file
from bot_helper.Database.User_Data import get_data, new_user, saveconfig, saveoptions, resetdatabase
from os.path import exists
from bot_helper.Telegram.Telegram_Client import Telegram




#////////////////////////////////////Variables////////////////////////////////////#
sudo_users = Config.SUDO_USERS
encoders_list = ['libx265', 'libx264']
# Added from VFBITMOD-update
vbit_list = ['8Bit', '10Bit']
acodec_list = ['AAC', 'OPUS', 'DD', 'DDP']
abit_list = ['64k', '96k', '128k', '160k', '192k', '256k', '320k', '512k', '640k', '768k', '960k']
achannel_list = ['2', '6']
qubality_list = ['480p [720x360]', '480p [720x480]', '720p [1280x640]', '720p [1280x720]', '1080p [1920x960]', '1080p [1920x1080]']
encode_list = ['Video', 'Audio', 'Video Audio [Both]']
encude_list = ['H.264', 'HEVC']
type_list = ['CRF', 'VBR']
# End of Added from VFBITMOD-update
crf_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51']
wsize_list =['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
presets_list =  ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
bool_list = [True, False]
ws_name = {'5:5': 'Top Left', 'main_w-overlay_w-5:5': 'Top Right', '5:main_h-overlay_h': 'Bottom Left', 'main_w-overlay_w-5:main_h-overlay_h-5': 'Bottom Right'}
ws_value = {'Top Left': '5:5', 'Top Right': 'main_w-overlay_w-5:5', 'Bottom Left': '5:main_h-overlay_h', 'Bottom Right': 'main_w-overlay_w-5:main_h-overlay_h-5'}
# REMOVED: TELETHON_CLIENT variable (no longer needed)
# TELETHON_CLIENT = Telegram.TELETHON_CLIENT
punc = ['!', '|', '{', '}', ';', ':', "'", '=', '"', '\\', ',', '<', '>', '/', '?', '@', '#', '$', '%', '^', '&', '*', '~', "  ", "\t", "+", "b'", "'"]
SAVE_TO_DATABASE = Config.SAVE_TO_DATABASE
LOGGER = Config.LOGGER


#////////////////////////////////////Callbacks////////////////////////////////////#
# MODIFIED: Removed TELETHON_CLIENT reference
@Telegram.PYROGRAM_CLIENT.on_callback_query() # Use Pyrogram decorator
async def callback(client, event): # Use Pyrogram arguments
        txt = event.data # Use event.data directly
        chat_id = event.message.chat.id # Use event.message.chat.id
        user_id = event.from_user.id # Use event.from_user.id
        if user_id not in get_data():
            await new_user(user_id, SAVE_TO_DATABASE)

        # Ensure user data has new keys before accessing callbacks
        user_data = get_data().get(user_id, {}) # Use .get() for safety
        if 'video' not in user_data:
            await saveconfig(user_id, 'video', 'qubality', '480p [720x480]', SAVE_TO_DATABASE)
            await saveconfig(user_id, 'video', 'encude', 'HEVC', SAVE_TO_DATABASE)
            await saveconfig(user_id, 'video', 'vbit', '8Bit', SAVE_TO_DATABASE)
        if 'audio' not in user_data:
             await saveconfig(user_id, 'audio', 'achannel', '2', SAVE_TO_DATABASE)
             await saveconfig(user_id, 'audio', 'acodec', 'AAC', SAVE_TO_DATABASE)
        if 'use_vbr' not in user_data:
            await saveoptions(user_id, 'use_vbr', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'vbr', '220k', SAVE_TO_DATABASE)
        if 'use_crf' not in user_data:
            await saveoptions(user_id, 'use_crf', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'crf', '22', SAVE_TO_DATABASE)
        if 'use_abit' not in user_data:
            await saveoptions(user_id, 'use_abit', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'abit', '128k', SAVE_TO_DATABASE)
        if 'convert' not in user_data or 'type' not in user_data.get('convert', {}):
             await saveconfig(user_id, 'convert', 'type', 'CRF', SAVE_TO_DATABASE)
        if 'convert' not in user_data or 'encode' not in user_data.get('convert', {}):
             await saveconfig(user_id, 'convert', 'encode', 'Video', SAVE_TO_DATABASE)
        # --- End of Key Check ---

        if txt.startswith("settings"):
            text = f"⚙ Hi {get_mention(event)} Choose Your Settings"
            # MODIFIED: Use event.edit_message_text for Pyrogram
            await event.edit_message_text(text, reply_markup=InlineKeyboardMarkup([ # Use Pyrogram InlineKeyboardMarkup
                [InlineKeyboardButton('#️⃣ General', callback_data='general_settings')], # Use Pyrogram InlineKeyboardButton
                # [InlineKeyboardButton('❣ Telegram', callback_data='telegram_settings')], # REMOVED: Telegram settings button
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

        elif txt=="close_settings":
            await event.message.delete() # Use event.message.delete()
            return

        elif txt.startswith("resetdb"):
            new_position = eval(txt.split("_", 1)[1])
            if new_position:
                reset = await resetdatabase(SAVE_TO_DATABASE)
                if reset:
                    text = f"✔Database Reset Successfull"
                else:
                    text = f"❌Database Reset Failed"
                await event.answer(text, show_alert=True) # Use show_alert=True
            else:
                await event.answer(f"Why You Wasting My Time.", show_alert=True)
            return


        elif txt.startswith("env"):
            position = txt.split("_", 1)[1]
            # MODIFIED: Need to adapt get_text_data for Pyrogram or implement differently
            # value_result = await get_text_data(chat_id, user_id, event, 120, f"Send New Value For Variable {position}")
            await event.answer("Environment variable editing needs adaptation for Pyrogram.", show_alert=True) # Placeholder
            # if value_result:
            #     if exists("./userdata/botconfig.env"):
            #         config_dict = get_env_dict('./userdata/botconfig.env')
            #     else:
            #         config_dict = get_env_dict('config.env')
            #     config_dict[position] = value_result.message.text # Use .text for Pyrogram
            #     export_env_file("./userdata/botconfig.env", config_dict)
            #     await value_result.reply(f"✅{position} Value Changed Successfully, Restart Bot To Reflect Changes.")
            return


        elif txt.startswith("renew"):
            new_position = eval(txt.split("_", 1)[1])
            if new_position:
                if exists(Config.DOWNLOAD_DIR):
                    await delete_all(Config.DOWNLOAD_DIR)
                    text = f"✔Successfully Deleted {Config.DOWNLOAD_DIR}"
                    try:
                            await event.answer(text, show_alert=True)
                    except:
                         # MODIFIED: Use event.edit_message_text
                        await event.edit_message_text(text)
                else:
                    await event.answer(f"Nothing to clear 🙄", show_alert=True)
                    return
            else:
                await event.answer(f"Why You Wasting My Time.", show_alert=True)
                return


        elif txt.startswith("general"):
            await general_callback(client, event, txt, user_id, chat_id) # Pass client
            return

        # REMOVED: Telegram callback trigger
        # elif txt.startswith("telegram"):
        #     await telegram_callback(event, txt, user_id, chat_id)
        #     return

        elif txt.startswith("vbrcrf"):
            await vbrcrf_callback(client, event, txt, user_id, chat_id) # Pass client
            return

        elif txt.startswith("progress"):
            await progress_callback(client, event, txt, user_id) # Pass client
            return

        elif txt.startswith("convert"):
            await convert_callback(client, event, txt, user_id, True) # Pass client
            return

        elif txt.startswith("video"):
            await video_callback(client, event, txt, user_id, True) # Pass client
            return

        elif txt.startswith("audio"):
            await audio_callback(client, event, txt, user_id, chat_id, True) # Pass client
            return

        elif txt.startswith("hardmux"):
            await hardmux_callback(client, event, txt, user_id, True) # Pass client
            return

        elif txt.startswith("softmux"):
            await softmux_callback(client, event, txt, user_id, True) # Pass client
            return

        elif txt.startswith("merge"):
            await merge_callback(client, event, txt, user_id) # Pass client
            return

        elif txt=="nik66bots":
            await event.answer(f"⚡Bot By Sahil⚡", show_alert=True)
            return


        elif txt.startswith("change"):
             # MODIFIED: Need to adapt get_text_data for Pyrogram or implement differently
            await event.answer("Queue size changing needs adaptation for Pyrogram.", show_alert=True) # Placeholder
            # if "_queue_size" in txt:
            #     queue_size_input= await get_text_data(chat_id, user_id, event, 120, "Send Queue Size")
            #     if queue_size_input:
            #         try:
            #             queue_size = int(queue_size_input.message.text) # Use .text
            #         except:
            #             await queue_size_input.reply("❗Invalid Input")
            #             return
            #         if txt=="change_convert_queue_size":
            #             await saveconfig(user_id, 'convert', 'queue_size', str(queue_size), SAVE_TO_DATABASE)
            #             await convert_callback(client, event, "convert_settings", user_id, False) # Pass client
            #         elif txt=="change_hardmux_queue_size":
            #             await saveconfig(user_id, 'hardmux', 'queue_size', str(queue_size), SAVE_TO_DATABASE)
            #             await hardmux_callback(client, event, "hardmux_settings", user_id, False) # Pass client
            return


        elif txt=="custom_metedata":
            cmetadata = get_data().get(user_id, {}).get('metadata', "Nik66Bots")
            await event.answer(f"✅Current Metadata: {str(cmetadata)}", show_alert=True)
            return

        elif txt=="vbr_value":
            cvbr = get_data().get(user_id, {}).get('vbr', '220k')
            await event.answer(f"❤ Current VBR 🖤: {str(cvbr)}", show_alert=True)
            return

        elif txt=="crf_value":
            ccrf = get_data().get(user_id, {}).get('crf', '22')
            await event.answer(f"❤ Current CRF 🖤: {str(ccrf)}", show_alert=True)
            return

        elif txt=="abit_value":
            cabit = get_data().get(user_id, {}).get('abit', '128k')
            await event.answer(f"❤ Current AudioBit 🖤: {str(cabit)}", show_alert=True)
            return


        return


#////////////////////////////////////Functions////////////////////////////////////#
# MODIFIED: Use Pyrogram event structure
def get_mention(event):
    return f"[{event.from_user.first_name}](tg://user?id={event.from_user.id})"

# MODIFIED: Import Pyrogram types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def gen_keyboard(values_list, current_value, callvalue, items, hide):
    boards = []
    lists = len(values_list)//items
    if lists!=len(values_list)/items:
        lists +=1
    current_list = []
    for x in values_list:
        if len(current_list)==items:
            boards.append(current_list)
            current_list = []
        value = f"{str(callvalue)}_{str(x)}"
        # REMOVED: Watermark specific logic
        # if current_value!=x:
        #     if callvalue!="watermarkposition":
        #         text = f"{str(x)}"
        #     else:
        #             text = f"{str(ws_name[x])}"
        # else:
        #     if not hide:
        #         if callvalue!="watermarkposition":
        #             text = f"{str(x)} 🟢"
        #         else:
        #             text = f"{str(ws_name[x])} 🟢"
        #     else:
        #         text = f"🟢"
        # MODIFIED: Simplified text generation
        text = f"{str(x)}"
        if current_value == x:
            text += " 🟢"

        # MODIFIED: Use Pyrogram InlineKeyboardButton
        keyboard = InlineKeyboardButton(text, callback_data=value)
        current_list.append(keyboard)
    boards.append(current_list)
    return boards

# MODIFIED: Needs adaptation for Pyrogram conversation/input handling
async def get_metadata(chat_id, user_id, event, timeout, message):
    # Placeholder - Pyrogram conversation logic is different
    await event.answer("Metadata input needs adaptation for Pyrogram.", show_alert=True)
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs adaptation for Pyrogram conversation/input handling
async def get_vbr(chat_id, user_id, event, timeout, message):
    # Placeholder - Pyrogram conversation logic is different
    await event.answer("VBR input needs adaptation for Pyrogram.", show_alert=True)
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs adaptation for Pyrogram conversation/input handling
async def get_crf(chat_id, user_id, event, timeout, message):
     # Placeholder - Pyrogram conversation logic is different
    await event.answer("CRF input needs adaptation for Pyrogram.", show_alert=True)
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs adaptation for Pyrogram conversation/input handling
async def get_abit(chat_id, user_id, event, timeout, message):
     # Placeholder - Pyrogram conversation logic is different
    await event.answer("AudioBit input needs adaptation for Pyrogram.", show_alert=True)
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...

# MODIFIED: Needs adaptation for Pyrogram conversation/input handling
async def get_text_data(chat_id, user_id, event, timeout, message):
    # Placeholder - Pyrogram conversation logic is different
    await event.answer("Text input needs adaptation for Pyrogram.", show_alert=True)
    return False
    # async with TELETHON_CLIENT.conversation(chat_id) as conv:
    #         ... (Telethon logic removed) ...


#////////////////////////////////////Callbacks_Functions////////////////////////////////////#

# REMOVED: telegram_callback function
# ###############------General------###############
# async def telegram_callback(event, txt, user_id, chat_id):
#             ... (function content removed) ...

# MODIFIED: Add client argument
###############------General------###############
async def general_callback(client, event, txt, user_id, chat_id):
            new_position = txt.split("_", 1)[1]
            r_config = f'./userdata/{str(user_id)}_rclone.conf'
            check_config = exists(r_config)
            user_data = get_data().get(user_id, {}) # Use .get()
            drive_name = user_data.get('drive_name', False) # Use .get()
            edit = True
            if txt.startswith("generalcustommetadata"): # MODIFIED: Adjusted elif chain
                if eval(new_position):
                        # MODIFIED: Needs adaptation for Pyrogram
                        # metadata = await get_metadata(chat_id, user_id, event, 120, "Send Metadata Title")
                        await event.answer("Metadata input needs adaptation for Pyrogram.", show_alert=True) # Placeholder
                        metadata = None # Placeholder
                        if metadata:
                            await saveoptions(user_id, 'metadata', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'custom_metadata', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Custom Metadata - {str(new_position)}", show_alert=True)
            elif txt.startswith("generaluploadtg"):
                if not eval(new_position):
                    if not (check_config and drive_name):
                        await event.answer(f"❗First Save Rclone ConfigFile/Account", show_alert=True)
                        return
                await saveoptions(user_id, 'upload_tg', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Upload On TG - {str(new_position)}", show_alert=True)
            elif txt.startswith("generaldrivename"):
                await saveoptions(user_id, 'drive_name', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Rclone Account - {str(new_position)}", show_alert=True)
            elif txt.startswith("generalautodrive"):
                if eval(new_position):
                    if not (check_config and drive_name):
                        await event.answer(f"❗First Save Rclone ConfigFile/Account", show_alert=True)
                        return
                await saveoptions(user_id, 'auto_drive', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Auto Upload Big File To Drive - {str(new_position)}", show_alert=True)
            elif txt.startswith("generalgenss"):
                await saveoptions(user_id, 'gen_ss', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Generate Screenshots - {str(new_position)}", show_alert=True)
            elif txt.startswith("generalssno"):
                await saveoptions(user_id, 'ss_no', int(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅No Of Screenshots - {str(new_position)}", show_alert=True)
            elif txt.startswith("generalgensample"):
                await saveoptions(user_id, 'gen_sample', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Generate Sample Video - {str(new_position)}", show_alert=True)

            # Use .get() with defaults for all settings
            user_data = get_data().get(user_id, {})
            upload_tg = user_data.get('upload_tg', True)
            custom_metadata = user_data.get('custom_metadata', False)
            drive_name = user_data.get('drive_name', False)
            auto_drive = user_data.get('auto_drive', False)
            gen_ss = user_data.get('gen_ss', False)
            ss_no = user_data.get('ss_no', 5)
            gen_sample = user_data.get('gen_sample', False)

            KeyBoard = []
            KeyBoard.append([InlineKeyboardButton(f'🪀Custom Metadata - {str(custom_metadata)} [Click To See]', callback_data='custom_metedata')])
            for board in gen_keyboard(bool_list, custom_metadata, "generalcustommetadata", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🧵Upload On TG - {str(upload_tg)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, upload_tg, "generaluploadtg", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🕹Auto Upload Big File To Drive - {str(auto_drive)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, auto_drive, "generalautodrive", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'📷Generate Screenshots - {str(gen_ss)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, gen_ss, "generalgenss", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🎶No Of Screenshots - {str(ss_no)}', callback_data='nik66bots')])
            for board in gen_keyboard([3,5,7,10], ss_no, "generalssno", 4, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🎞Generate Sample Video - {str(gen_sample)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, gen_sample, "generalgensample", 2, False):
                KeyBoard.append(board)
            if check_config:
                accounts = await get_config(r_config)
                if accounts:
                    KeyBoard.append([InlineKeyboardButton(f'🔮Rclone Account - {str(drive_name)}', callback_data='nik66bots')])
                    for board in gen_keyboard(accounts, drive_name, "generaldrivename", 2, False):
                        KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                    # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("⚙ General Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(chat_id, "⚙ General Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return

# MODIFIED: Add client argument
###############------Progress------###############
async def progress_callback(client, event, txt, user_id):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("progressdetailedprogress"):
                await saveoptions(user_id, 'detailed_messages', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Detailed Messages - {str(new_position)}", show_alert=True)
            elif txt.startswith("progressshowstats"):
                await saveoptions(user_id, 'show_stats', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Stats - {str(new_position)}", show_alert=True)
            elif txt.startswith("progressupdatetime"):
                await saveoptions(user_id, 'update_time', int(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Progress Update Time - {str(new_position)} secs", show_alert=True)
            elif txt.startswith("progressffmpegsize"):
                await saveoptions(user_id, 'ffmpeg_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show FFMPEG Output File Size - {str(new_position)}", show_alert=True)
            elif txt.startswith("progressffmpegptime"):
                await saveoptions(user_id, 'ffmpeg_ptime', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Process Time - {str(new_position)}", show_alert=True)
            elif txt.startswith("progressshowtime"):
                await saveoptions(user_id, 'show_time', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Current Time - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            user_data = get_data().get(user_id, {})
            detailed_messages = user_data.get('detailed_messages', True)
            show_stats = user_data.get('show_stats', True)
            update_time = user_data.get('update_time', 7)
            ffmpeg_size = user_data.get('ffmpeg_size', True)
            ffmpeg_ptime = user_data.get('ffmpeg_ptime', True)
            show_time = user_data.get('show_time', True)

            KeyBoard.append([InlineKeyboardButton(f'📋Show Detailed Messages - {str(detailed_messages)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, detailed_messages, "progressdetailedprogress", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'📊Show Stats - {str(show_stats)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, show_stats, "progressshowstats", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'📀Show FFMPEG Output File Size - {str(ffmpeg_size)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, ffmpeg_size, "progressffmpegsize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'⏲Show Process Time- {str(ffmpeg_ptime)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, ffmpeg_ptime, "progressffmpegptime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'⌚Show Current Time- {str(show_time)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, show_time, "progressshowtime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'⏱Progress Update Time - {str(update_time)} secs', callback_data='nik66bots')])
            for board in gen_keyboard([5, 6, 7, 8, 9, 10], update_time, "progressupdatetime", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            try:
                 # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                await event.edit_message_text("⚙ Progress Bar Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            except:
                pass
            return

# REMOVED: compress_callback function

# MODIFIED: Add client argument
###############------Merge------###############
async def merge_callback(client, event, txt, user_id):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("mergemap"):
                await saveconfig(user_id, 'merge', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Merge Map - {str(new_position)}", show_alert=True)
            elif txt.startswith("mergefixblank"):
                await saveconfig(user_id, 'merge', 'fix_blank', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Merge Fix Blank - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            merge_settings = get_data().get(user_id, {}).get('merge', {})
            merge_map = merge_settings.get('map', True)
            merge_fix_blank = merge_settings.get('fix_blank', False)

            KeyBoard.append([InlineKeyboardButton(f'🍓Map  - {str(merge_map)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, merge_map, "mergemap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🚢Fix Blank Outro  - {str(merge_fix_blank)} [Use Only When Necessary]', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, merge_fix_blank, "mergefixblank", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            try:
                 # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                await event.edit_message_text("⚙ Merge Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            except:
                pass
            return

# MODIFIED: Add client argument
###############------Convert------###############
async def convert_callback(client, event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            # Added from VFBITMOD-update
            if txt.startswith("convertencode"):
                await saveconfig(user_id, 'convert', 'encode', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Encode - {str(new_position)}", show_alert=True)
            elif txt.startswith("converttype"):
                await saveconfig(user_id, 'convert', 'type', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Encode Type - {str(new_position)}", show_alert=True)
            # End of Added from VFBITMOD-update
            elif txt.startswith("convertpreset"):
                await saveconfig(user_id, 'convert', 'preset', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Preset - {str(new_position)}", show_alert=True)
            elif txt.startswith("convertcopysub"):
                await saveconfig(user_id, 'convert', 'copy_sub', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Copy Subtitles - {str(new_position)}", show_alert=True)
            elif txt.startswith("convertmap"):
                await saveconfig(user_id, 'convert', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Map - {str(new_position)}", show_alert=True)
            elif txt.startswith("convertusequeuesize"):
                await saveconfig(user_id, 'convert', 'use_queue_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Use Queue Size - {str(new_position)}", show_alert=True)
            elif txt.startswith("convertsync"):
                await saveconfig(user_id, 'convert', 'sync', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Use SYNC - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            convert_settings = get_data().get(user_id, {}).get('convert', {})
            convert_encode = convert_settings.get('encode', 'Video')
            convert_type = convert_settings.get('type', 'CRF')
            convert_preset = convert_settings.get('preset', 'ultrafast')
            convert_map = convert_settings.get('map', True)
            convert_copysub = convert_settings.get('copy_sub', False)
            convert_use_queue_size = convert_settings.get('use_queue_size', False)
            convert_queue_size = convert_settings.get('queue_size', '9999')
            convert_sync = convert_settings.get('sync', False)

            # Added from VFBITMOD-update
            KeyBoard.append([InlineKeyboardButton(f'🎧Encode - {str(convert_encode)}', callback_data='nik66bots')])
            for board in gen_keyboard(encode_list, convert_encode, "convertencode", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🎧Encode Type - {str(convert_type)}', callback_data='nik66bots')])
            for board in gen_keyboard(type_list, convert_type, "converttype", 2, False):
                KeyBoard.append(board)
            # End of Added from VFBITMOD-update

            KeyBoard.append([InlineKeyboardButton(f'🍄Copy Subtitles - {str(convert_copysub)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, convert_copysub, "convertcopysub", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🍓Map  - {str(convert_map)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, convert_map, "convertmap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'📻Use FFMPEG Queue Size  - {str(convert_use_queue_size)}', callback_data='nik66bots')])
            if convert_use_queue_size:
                KeyBoard.append([InlineKeyboardButton(f'🎹FFMPEG Queue Size Value  - {str(convert_queue_size)} (Click To Change)', callback_data='change_convert_queue_size')])
            for board in gen_keyboard(bool_list, convert_use_queue_size, "convertusequeuesize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🌳Use SYNC - {str(convert_sync)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, convert_sync, "convertsync", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'♒Preset - {str(convert_preset)}', callback_data='nik66bots')])
            for board in gen_keyboard(presets_list, convert_preset, "convertpreset", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                     # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("⚙ Convert Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                try:
                    await event.message.delete() # Use event.message.delete()
                except:
                    pass
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(event.message.chat.id, "⚙ Convert Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return

# MODIFIED: Add client argument
###############------Hardmux------###############
async def hardmux_callback(client, event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("hardmuxencoder"):
                await saveconfig(user_id, 'hardmux', 'encoder', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Encoder - {str(new_position)}", show_alert=True)
            elif txt.startswith("hardmuxencodevideo"):
                await saveconfig(user_id, 'hardmux', 'encode_video', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Use Encoder - {str(new_position)}", show_alert=True)
            elif txt.startswith("hardmuxpreset"):
                await saveconfig(user_id, 'hardmux', 'preset', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Preset - {str(new_position)}", show_alert=True)
            elif txt.startswith("hardmuxcrf"):
                await saveconfig(user_id, 'hardmux', 'crf', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux CRF - {str(new_position)}", show_alert=True)
            elif txt.startswith("hardmuxusequeuesize"):
                await saveconfig(user_id, 'hardmux', 'use_queue_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Use Queue Size - {str(new_position)}", show_alert=True)
            elif txt.startswith("hardmuxsync"):
                await saveconfig(user_id, 'hardmux', 'sync', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Use SYNC - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            hardmux_settings = get_data().get(user_id, {}).get('hardmux', {})
            hardmux_encode_video = hardmux_settings.get('encode_video', True)
            hardmux_encoder = hardmux_settings.get('encoder', 'libx265')
            hardmux_preset = hardmux_settings.get('preset', 'ultrafast')
            hardmux_crf = hardmux_settings.get('crf', '23')
            hardmux_use_queue_size = hardmux_settings.get('use_queue_size', False)
            hardmux_queue_size = hardmux_settings.get('queue_size', '9999')
            hardmux_sync = hardmux_settings.get('sync', False)

            KeyBoard.append([InlineKeyboardButton(f'🎧Use Encoder - {str(hardmux_encode_video)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, hardmux_encode_video, "hardmuxencodevideo", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🍬Encoder - {str(hardmux_encoder)}', callback_data='nik66bots')])
            for board in gen_keyboard(encoders_list, hardmux_encoder, "hardmuxencoder", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'📻Use FFMPEG Queue Size  - {str(hardmux_use_queue_size)}', callback_data='nik66bots')])
            if hardmux_use_queue_size:
                KeyBoard.append([InlineKeyboardButton(f'🎹FFMPEG Queue Size Value  - {str(hardmux_queue_size)} (Click To Change)', callback_data='change_hardmux_queue_size')])
            for board in gen_keyboard(bool_list, hardmux_use_queue_size, "hardmuxusequeuesize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🌳Use SYNC - {str(hardmux_sync)}', callback_data='nik66bots')])
            for board in gen_keyboard(bool_list, hardmux_sync, "hardmuxsync", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'♒Preset - {str(hardmux_preset)}', callback_data='nik66bots')])
            for board in gen_keyboard(presets_list, hardmux_preset, "hardmuxpreset", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'⚡CRF  - {str(hardmux_crf)}', callback_data='nik66bots')])
            for board in gen_keyboard(crf_list, hardmux_crf, "hardmuxcrf", 6, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                     # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("⚙ Hardmux Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                try:
                    await event.message.delete() # Use event.message.delete()
                except:
                    pass
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(event.message.chat.id, "⚙ Hardmux Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return

# MODIFIED: Add client argument
###############------Softmux------###############
async def softmux_callback(client, event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("softmuxsubcodec"):
                await saveconfig(user_id, 'softmux', 'sub_codec', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Softmux Sub Codec - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            softmux_settings = get_data().get(user_id, {}).get('softmux', {})
            softmux_sub_codec = softmux_settings.get('sub_codec', 'copy')

            KeyBoard.append([InlineKeyboardButton(f'🍄Subtitles Codec - {str(softmux_sub_codec)}', callback_data='nik66bots')])
            for board in gen_keyboard(['copy', 'mov_text'], softmux_sub_codec, "softmuxsubcodec", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                     # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("⚙ Softmux Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                try:
                    await event.message.delete() # Use event.message.delete()
                except:
                    pass
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(event.message.chat.id, "⚙ Softmux Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return

# REMOVED: softremux_callback function

# Added from VFBITMOD-update
# MODIFIED: Add client argument
###############------Video------###############
async def video_callback(client, event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("videoencude"):
                await saveconfig(user_id, 'video', 'encude', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅FOrmant - {str(new_position)}", show_alert=True)
            elif txt.startswith("videovbit"):
                await saveconfig(user_id, 'video', 'vbit', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert VideoBit - {str(new_position)}", show_alert=True)
            elif txt.startswith("videoquality"):
                await saveconfig(user_id, 'video', 'qubality', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Quality - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            video_settings = get_data().get(user_id, {}).get('video', {})
            video_vbit = video_settings.get('vbit', '8Bit')
            video_encude = video_settings.get('encude', 'HEVC')
            video_qubality = video_settings.get('qubality', '480p [720x480]')

            KeyBoard.append([InlineKeyboardButton(f'❤ Encoder - {str(video_encude)}', callback_data='nik66bots')])
            for board in gen_keyboard(encude_list, video_encude, "videoencude", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'❤ VideoBit - {str(video_vbit)}', callback_data='nik66bots')])
            for board in gen_keyboard(vbit_list, video_vbit, "videovbit", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'❤ Resolution - {str(video_qubality)}', callback_data='nik66bots')])
            for board in gen_keyboard(qubality_list, video_qubality, "videoquality", 2, False):
                KeyBoard.append(board)

            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                     # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("🎬 Video Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                try:
                    await event.message.delete() # Use event.message.delete()
                except:
                    pass
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(event.message.chat.id, "🎬 Video Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return

# MODIFIED: Add client argument
###############-----Audio------###############
async def audio_callback(client, event, txt, user_id, chat_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("audioachannel"):
                await saveconfig(user_id, 'audio', 'achannel', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Audio Channel - {str(new_position)}", show_alert=True)
            elif txt.startswith("audioacodec"):
                await saveconfig(user_id, 'audio', 'acodec', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Audio codec - {str(new_position)}", show_alert=True)
            elif txt.startswith("audioabit"):
                if eval(new_position):
                        # MODIFIED: Needs adaptation for Pyrogram
                        # metadata = await get_abit(chat_id, user_id, event, 120, "**Send AudioBit Value\n\n****Example :** `128k`, `760k` etc.")
                        await event.answer("AudioBit input needs adaptation for Pyrogram.", show_alert=True) # Placeholder
                        metadata = None # Placeholder
                        if metadata:
                            await saveoptions(user_id, 'abit', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_abit', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ AudioBit 🖤 - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            user_data = get_data().get(user_id, {})
            audio_settings = user_data.get('audio', {})
            use_abit = user_data.get('use_abit', False)
            audio_acodec = audio_settings.get('acodec', 'AAC')
            audio_achannel = audio_settings.get('achannel', '2')

            KeyBoard.append([InlineKeyboardButton(f'🖤 Audio Codec - {str(audio_acodec)}', callback_data='nik66bots')])
            for board in gen_keyboard(acodec_list, audio_acodec, "audioacodec", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🖤 Audio Channel - {str(audio_achannel)}', callback_data='nik66bots')])
            for board in gen_keyboard(achannel_list, audio_achannel, "audioachannel", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🖤 AudioBit - {str(use_abit)} [Click To See]', callback_data='abit_value')])
            for board in gen_keyboard(bool_list, use_abit, "audioabit", 2, False):
                KeyBoard.append(board)

            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                     # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("🔊 Audio Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                try:
                    await event.message.delete() # Use event.message.delete()
                except:
                    pass
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(event.message.chat.id, "🔊 Audio Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return

# MODIFIED: Add client argument
###############-----CRF By Word------###############
async def vbrcrf_callback(client, event, txt, user_id, chat_id):
            new_position = txt.split("_", 1)[1]
            edit = True
            if txt.startswith("vbrcrfvbr"):
                if eval(new_position):
                        # MODIFIED: Needs adaptation for Pyrogram
                        # metadata = await get_vbr(chat_id, user_id, event, 120, "**Send VBR Value**\n\n**Example :** `400k`, `900k` etc.")
                        await event.answer("VBR input needs adaptation for Pyrogram.", show_alert=True) # Placeholder
                        metadata = None # Placeholder
                        if metadata:
                            await saveoptions(user_id, 'vbr', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_vbr', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ VBR 🖤 - {str(new_position)}", show_alert=True)
            elif txt.startswith("vbrcrfcrf"):
                if eval(new_position):
                        # MODIFIED: Needs adaptation for Pyrogram
                        # metadata = await get_crf(chat_id, user_id, event, 120, "**Send CRF Value**\n\n**Example :** `22`, `28` etc.")
                        await event.answer("CRF input needs adaptation for Pyrogram.", show_alert=True) # Placeholder
                        metadata = None # Placeholder
                        if metadata:
                            await saveoptions(user_id, 'crf', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_crf', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ CRF 🖤 - {str(new_position)}", show_alert=True)

            # Use .get() with defaults
            user_data = get_data().get(user_id, {})
            use_vbr = user_data.get('use_vbr', False)
            use_crf = user_data.get('use_crf', False)

            KeyBoard = []
            KeyBoard.append([InlineKeyboardButton(f'❤ VBR - {str(use_vbr)} [Click To See]', callback_data='vbr_value')])
            for board in gen_keyboard(bool_list, use_vbr, "vbrcrfvbr", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([InlineKeyboardButton(f'🖤 CRF - {str(use_crf)} [Click To See]', callback_data='crf_value')])
            for board in gen_keyboard(bool_list, use_crf, "vbrcrfcrf", 2, False):
                KeyBoard.append(board)

            KeyBoard.append([InlineKeyboardButton(f'↩Back', callback_data='settings')])
            if edit:
                try:
                     # MODIFIED: Use event.edit_message_text and InlineKeyboardMarkup
                    await event.edit_message_text("❤ VBR / 🖤 CRF Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
                except:
                    pass
            else:
                 # MODIFIED: Use client.send_message and InlineKeyboardMarkup
                await client.send_message(chat_id, "❤ VBR / 🖤 CRF Settings", reply_markup=InlineKeyboardMarkup(KeyBoard))
            return
# End of Added from VFBITMOD-update

# --- END OF FILE VideoFlux-Re-master/bot/callbacks.py ---
