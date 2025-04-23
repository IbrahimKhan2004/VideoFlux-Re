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
# Highlighted change: Added CBR to type_list
type_list = ['CRF', 'VBR', 'ABR', 'CBR'] # Added CBR
# End of Added from VFBITMOD-update
crf_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51']
wsize_list =['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
presets_list =  ['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow']
bool_list = [True, False]
ws_name = {'5:5': 'Top Left', 'main_w-overlay_w-5:5': 'Top Right', '5:main_h-overlay_h': 'Bottom Left', 'main_w-overlay_w-5:main_h-overlay_h-5': 'Bottom Right'}
ws_value = {'Top Left': '5:5', 'Top Right': 'main_w-overlay_w-5:5', 'Bottom Left': '5:main_h-overlay_h', 'Bottom Right': 'main_w-overlay_w-5:main_h-overlay_h-5'}
TELETHON_CLIENT = Telegram.TELETHON_CLIENT
punc = ['!', '|', '{', '}', ';', ':', "'", '=', '"', '\\', ',', '<', '>', '/', '?', '@', '#', '$', '%', '^', '&', '*', '~', "  ", "\t", "+", "b'", "'"]
SAVE_TO_DATABASE = Config.SAVE_TO_DATABASE
LOGGER = Config.LOGGER
# Highlighted change: Added upload destination list
upload_destination_list = ['Rclone', 'Gofile']
# End of highlighted change
# Highlighted change: Added tune list
tune_list = ['None', 'fastdecode', 'zerolatency', 'film', 'animation']
# End of highlighted change
# Highlighted change: Added processing unit list
processing_unit_list = ['CPU', 'GPU']
# End of highlighted change


#////////////////////////////////////Callbacks////////////////////////////////////#
@TELETHON_CLIENT.on(events.CallbackQuery)
async def callback(event):
        txt = event.data.decode()
        chat_id = event.chat.id
        user_id = event.sender.id
        if user_id not in get_data():
            await new_user(user_id, SAVE_TO_DATABASE)

        # Ensure user data has new keys before accessing callbacks
        user_data = get_data().get(user_id, {}) # Use .get() for safety
        if 'video' not in user_data:
            await saveconfig(user_id, 'video', 'qubality', '480p [720x480]', SAVE_TO_DATABASE)
            await saveconfig(user_id, 'video', 'encude', 'HEVC', SAVE_TO_DATABASE)
            await saveconfig(user_id, 'video', 'vbit', '8Bit', SAVE_TO_DATABASE)
# Highlighted change: Added check for tune key
            await saveconfig(user_id, 'video', 'tune', 'None', SAVE_TO_DATABASE) # Add default tune if video dict is missing
        elif 'tune' not in user_data.get('video', {}): # Check specifically if tune is missing within video dict
            await saveconfig(user_id, 'video', 'tune', 'None', SAVE_TO_DATABASE) # Add default tune
# End of highlighted change
        if 'audio' not in user_data:
             await saveconfig(user_id, 'audio', 'achannel', '2', SAVE_TO_DATABASE)
             await saveconfig(user_id, 'audio', 'acodec', 'AAC', SAVE_TO_DATABASE)
        if 'use_vbr' not in user_data:
            await saveoptions(user_id, 'use_vbr', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'vbr', '220k', SAVE_TO_DATABASE)
        if 'use_crf' not in user_data:
            await saveoptions(user_id, 'use_crf', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'crf', '22', SAVE_TO_DATABASE)
        # Added check for ABR keys
        if 'use_abr' not in user_data:
            await saveoptions(user_id, 'use_abr', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'abr', '1500k', SAVE_TO_DATABASE)
        # End of added check for ABR keys
        # Highlighted change: Added check for CBR keys
        if 'use_cbr' not in user_data:
            await saveoptions(user_id, 'use_cbr', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'cbr', '1500k', SAVE_TO_DATABASE)
        # End of added check for CBR keys
        if 'use_abit' not in user_data:
            await saveoptions(user_id, 'use_abit', False, SAVE_TO_DATABASE)
            await saveoptions(user_id, 'abit', '128k', SAVE_TO_DATABASE)
        if 'convert' not in user_data or 'type' not in user_data.get('convert', {}):
             await saveconfig(user_id, 'convert', 'type', 'CRF', SAVE_TO_DATABASE)
        if 'convert' not in user_data or 'encode' not in user_data.get('convert', {}):
             await saveconfig(user_id, 'convert', 'encode', 'Video', SAVE_TO_DATABASE)
# Highlighted change: Added check for upload_destination key
        if 'upload_destination' not in user_data:
            await saveoptions(user_id, 'upload_destination', 'Rclone', SAVE_TO_DATABASE)
# End of highlighted change
# Highlighted change: Added check for processing_unit key
        if 'processing_unit' not in user_data:
            await saveoptions(user_id, 'processing_unit', 'CPU', SAVE_TO_DATABASE)
# End of highlighted change
        # --- End of Key Check ---

        if txt.startswith("settings"):
            text = f"⚙ Hi {get_mention(event)} Choose Your Settings"
            await event.edit(text, buttons=[
            [Button.inline('#️⃣ General', 'general_settings')],
            [Button.inline('❣ Telegram', 'telegram_settings')],
            [Button.inline('📝 Progress Bar', 'progress_settings')],
            # [Button.inline('🏮 Compression', 'compression_settings')], # REMOVED: Compression button
            # [Button.inline('🛺 Watermark', 'watermark_settings')], # REMOVED: Watermark button
            [Button.inline('🍧 Merge', 'merge_settings')],
            # Modified menu items below based on VFBITMOD-update
            [Button.inline('💻 Encode', 'convert_settings')],
            [Button.inline('🎬 Video ', 'video_settings')],
            [Button.inline('🔊 Audio', 'audio_settings')],
            # Highlighted change: Updated button text for Rate Control
            [Button.inline('❤ Rate Control (VBR/CRF/ABR/CBR)', 'vbrcrf_settings')], # Modified button text
            # End of Modified menu items
            [Button.inline('🚍 HardMux', 'hardmux_settings')],
            [Button.inline('🎮 SoftMux', 'softmux_settings')],
            # [Button.inline('🛩SoftReMux', 'softremux_settings')], # REMOVED: SoftReMux button
            [Button.inline('⭕Close Settings', 'close_settings')]
        ])
            return

        elif txt=="close_settings":
            await event.delete()
            return

        elif txt.startswith("resetdb"):
            new_position = eval(txt.split("_", 1)[1])
            if new_position:
                reset = await resetdatabase(SAVE_TO_DATABASE)
                if reset:
                    text = f"✔Database Reset Successfull"
                else:
                    text = f"❌Database Reset Failed"
                await event.answer(text, alert=True)
            else:
                await event.answer(f"Why You Wasting My Time.", alert=True)
            return


        elif txt.startswith("env"):
            position = txt.split("_", 1)[1]
            value_result = await get_text_data(chat_id, user_id, event, 120, f"Send New Value For Variable {position}")
            if value_result:
                if exists("./userdata/botconfig.env"):
                    config_dict = get_env_dict('./userdata/botconfig.env')
                else:
                    config_dict = get_env_dict('config.env')
                config_dict[position] = value_result.message.message
                export_env_file("./userdata/botconfig.env", config_dict)
                await value_result.reply(f"✅{position} Value Changed Successfully, Restart Bot To Reflect Changes.")
            return


        elif txt.startswith("renew"):
            new_position = eval(txt.split("_", 1)[1])
            if new_position:
                if exists(Config.DOWNLOAD_DIR):
                    await delete_all(Config.DOWNLOAD_DIR)
                    text = f"✔Successfully Deleted {Config.DOWNLOAD_DIR}"
                    try:
                            await event.answer(text, alert=True)
                    except:
                        await event.edit(text)
                else:
                    await event.answer(f"Nothing to clear 🙄", alert=True)
                    return
            else:
                await event.answer(f"Why You Wasting My Time.", alert=True)
                return


        elif txt.startswith("general"):
            await general_callback(event, txt, user_id, chat_id)
            return

        # Added from VFBITMOD-update
        elif txt.startswith("vbrcrf"):
            await vbrcrf_callback(event, txt, user_id, chat_id)
            return
        # End of Added from VFBITMOD-update

        elif txt.startswith("telegram"):
            await telegram_callback(event, txt, user_id, chat_id)
            return

        elif txt.startswith("progress"):
            await progress_callback(event, txt, user_id)
            return

        # REMOVED: Compression callback trigger
        # elif txt.startswith("compression"):
        #     await compress_callback(event, txt, user_id, True)
        #     return

        elif txt.startswith("convert"):
            await convert_callback(event, txt, user_id, True)
            return

        # Added from VFBITMOD-update
        elif txt.startswith("video"):
            await video_callback(event, txt, user_id, True)
            return

        elif txt.startswith("audio"):
            await audio_callback(event, txt, user_id, chat_id, True)
            return
        # End of Added from VFBITMOD-update

        elif txt.startswith("hardmux"):
            await hardmux_callback(event, txt, user_id, True)
            return

        elif txt.startswith("softmux"):
            await softmux_callback(event, txt, user_id, True)
            return

        # REMOVED: SoftReMux callback trigger
        # elif txt.startswith("softremux"):
        #     await softremux_callback(event, txt, user_id, True)
        #     return

        elif txt.startswith("merge"):
            await merge_callback(event, txt, user_id)
            return

        # REMOVED: Watermark callback trigger
        # elif txt.startswith("watermark"):
        #     await watermark_callback(event, txt, user_id, True)
        #     return


        elif txt=="BashAFK":
            await event.answer(f"⚡Bot By BashAFK⚡", alert=True) # Kept original message
            return


        elif txt.startswith("change"):
            if "_queue_size" in txt:
                queue_size_input= await get_text_data(chat_id, user_id, event, 120, "Send Queue Size")
                if queue_size_input:
                    try:
                        queue_size = int(queue_size_input.message.message)
                    except:
                        await queue_size_input.reply("❗Invalid Input")
                        return
                    # REMOVED: Compress queue size change
                    # if txt=="change_compress_queue_size":
                    #     await saveconfig(user_id, 'compress', 'queue_size', str(queue_size), SAVE_TO_DATABASE)
                    #     await compress_callback(event, "compression_settings", user_id, False)
                    # REMOVED: Watermark queue size change
                    # elif txt=="change_watermark_queue_size":
                    #     await saveconfig(user_id, 'watermark', 'queue_size', str(queue_size), SAVE_TO_DATABASE)
                    #     await watermark_callback(event, "watermark_settings", user_id, False)
                    if txt=="change_convert_queue_size": # MODIFIED: Adjusted elif
                        await saveconfig(user_id, 'convert', 'queue_size', str(queue_size), SAVE_TO_DATABASE)
                        await convert_callback(event, "convert_settings", user_id, False)
                    elif txt=="change_hardmux_queue_size":
                        await saveconfig(user_id, 'hardmux', 'queue_size', str(queue_size), SAVE_TO_DATABASE)
                        await hardmux_callback(event, "hardmux_settings", user_id, False)
            return


        elif txt=="custom_metedata":
            cmetadata = get_data().get(user_id, {}).get('metadata', "BashAFK") # Use .get() with default
            await event.answer(f"✅Current Metadata: {str(cmetadata)}", alert=True) # Kept original message
            return

        # Added from VFBITMOD-update
        elif txt=="vbr_value":
            cvbr = get_data().get(user_id, {}).get('vbr', '220k') # Use .get() with default
            await event.answer(f"❤ Current VBR 🖤: {str(cvbr)}", alert=True)
            return

        elif txt=="crf_value":
            ccrf = get_data().get(user_id, {}).get('crf', '22') # Use .get() with default
            await event.answer(f"❤ Current CRF 🖤: {str(ccrf)}", alert=True)
            return

        # Added ABR value display
        elif txt=="abr_value":
            cabr = get_data().get(user_id, {}).get('abr', '1500k') # Use .get() with default
            await event.answer(f"❤ Current ABR 🖤: {str(cabr)}", alert=True)
            return

        # Highlighted change: Added CBR value display callback
        elif txt=="cbr_value":
            ccbr = get_data().get(user_id, {}).get('cbr', '1500k') # Use .get() with default
            await event.answer(f"❤ Current CBR 🖤: {str(ccbr)}", alert=True)
            return

        elif txt=="abit_value":
            cabit = get_data().get(user_id, {}).get('abit', '128k') # Use .get() with default
            await event.answer(f"❤ Current AudioBit 🖤: {str(cabit)}", alert=True)
            return
        # End of Added from VFBITMOD-update


        return


#////////////////////////////////////Functions////////////////////////////////////#
def get_mention(event):
    return "["+event.sender.first_name+"](tg://user?id="+str(event.sender.id)+")"

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
# Highlighted change: Explicitly cast to string for comparison
        if str(current_value) != str(x):
# End of highlighted change
            if callvalue!="watermarkposition":
                text = f"{str(x)}"
            else:
                    text = f"{str(ws_name[x])}"
        else:
            if not hide:
                if callvalue!="watermarkposition":
                    text = f"{str(x)} 🟢" # Kept original emoji
                else:
                    text = f"{str(ws_name[x])} 🟢" # Kept original emoji
            else:
                text = f"🟢" # Kept original emoji
        keyboard = Button.inline(text, value)
        current_list.append(keyboard)
    boards.append(current_list)
    return boards


async def get_metadata(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'*️⃣ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            metadata = new_event.message.message
            for ele in punc:
                if ele in metadata:
                        metadata = metadata.replace(ele, '')
            return metadata

# Added from VFBITMOD-update
async def get_vbr(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'❤ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🤦‍♂️Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            vbr = new_event.message.message
            for ele in punc:
                if ele in vbr:
                        vbr = vbr.replace(ele, '')
            return vbr

async def get_crf(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'❤ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🤦‍♂️Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            crf = new_event.message.message
            for ele in punc:
                if ele in crf:
                        crf = crf.replace(ele, '')
            return crf

# Added ABR input function
async def get_abr(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'❤ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🤦‍♂️Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            abr = new_event.message.message
            for ele in punc:
                if ele in abr:
                        abr = abr.replace(ele, '')
            # Basic validation (ends with 'k' or 'M') - can be improved
            if not (abr.lower().endswith('k') or abr.lower().endswith('m')):
                await new_event.reply('❗Invalid format. Use k or M (e.g., 1500k, 2M).')
                return False
            return abr

# Highlighted change: Added CBR input function
async def get_cbr(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'❤ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🤦‍♂️Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            cbr = new_event.message.message
            for ele in punc:
                if ele in cbr:
                        cbr = cbr.replace(ele, '')
            # Basic validation (ends with 'k' or 'M') - can be improved
            if not (cbr.lower().endswith('k') or cbr.lower().endswith('m')):
                await new_event.reply('❗Invalid format. Use k or M (e.g., 1500k, 2M).')
                return False
            return cbr

async def get_abit(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'❤ {str(message)} [{str(timeout)} secs]')
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🤦‍♂️Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            abit = new_event.message.message
            for ele in punc:
                if ele in abit:
                        abit = abit.replace(ele, '')
            return abit
# End of Added from VFBITMOD-update

async def get_text_data(chat_id, user_id, event, timeout, message):
    async with TELETHON_CLIENT.conversation(chat_id) as conv:
            handle = conv.wait_event(events.NewMessage(chats=chat_id, incoming=True, from_users=[user_id], func=lambda e: e.message.message), timeout=timeout)
            ask = await event.reply(f'*️⃣ {str(message)} [{str(timeout)} secs]') # Kept original emoji
            try:
                new_event = await handle
            except Exception as e:
                await ask.reply('🔃Timed Out! Tasked Has Been Cancelled.')
                LOGGER.info(e)
                return False
            return new_event


#////////////////////////////////////Callbacks_Functions////////////////////////////////////#


###############------General------###############
async def telegram_callback(event, txt, user_id, chat_id):
            new_position = txt.split("_", 1)[1]
            if txt.startswith("telegramupload"):
                await saveoptions(user_id, 'tgupload', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Telegram Upload Client - {str(new_position)}")
            elif txt.startswith("telegramdownload"):
                await saveoptions(user_id, 'tgdownload', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Telegram Download Client - {str(new_position)}")
            telegram_upload = get_data().get(user_id, {}).get('tgupload', "Pyrogram") # Use .get()
            telegram_download = get_data().get(user_id, {}).get('tgdownload', "Pyrogram") # Use .get()
            KeyBoard = []
            KeyBoard.append([Button.inline(f'🔼Telegram Upload Client - {str(telegram_upload)}', 'BashAFK')])
            for board in gen_keyboard(["Telethon", "Pyrogram"], telegram_upload, "telegramupload", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🔽Telegram Download Client - {str(telegram_download)}', 'BashAFK')])
            for board in gen_keyboard(["Telethon", "Pyrogram"], telegram_download, "telegramdownload", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            try:
                await event.edit("⚙ Telegram Settings", buttons=KeyBoard)
            except:
                pass
            return

###############------General------###############
async def general_callback(event, txt, user_id, chat_id):
# Highlighted change: Define prefix before using it
            callback_prefix = "generalupload_destination_"
# End of highlighted change
            new_position = txt.split("_", 1)[1]
            r_config = f'./userdata/{str(user_id)}_rclone.conf'
            check_config = exists(r_config)
            user_data = get_data().get(user_id, {}) # Use .get()
            drive_name = user_data.get('drive_name', False) # Use .get()
            edit = True
            # REMOVED: Audio selection logic
            # if txt.startswith("generalselectstream"):
            #     await saveoptions(user_id, 'select_stream', eval(new_position), SAVE_TO_DATABASE)
            #     await event.answer(f"✅Auto Select Audio - {str(new_position)}")
            # elif txt.startswith("generalstream"):
            #     await saveoptions(user_id, 'stream', new_position, SAVE_TO_DATABASE)
            #     await event.answer(f"✅Select Audio - {str(new_position)}")
            # REMOVED: Split logic
            # elif txt.startswith("generalsplitvideo"):
            #     await saveoptions(user_id, 'split_video', eval(new_position), SAVE_TO_DATABASE)
            #     await event.answer(f"✅Split Video - {str(new_position)}")
            # elif txt.startswith("generalsplit"):
            #     await saveoptions(user_id, 'split', new_position, SAVE_TO_DATABASE)
            #     await event.answer(f"✅Split Size - {str(new_position)}")
            # REMOVED: Dynamic thumbnail logic
            # elif txt.startswith("generalcustomthumbnail"):
            #     await saveoptions(user_id, 'custom_thumbnail', eval(new_position), SAVE_TO_DATABASE)
            #     await event.answer(f"✅Dynamic Thumbnail - {str(new_position)}")
            if txt.startswith("generalcustommetadata"): # MODIFIED: Adjusted elif chain
                if eval(new_position):
                        metadata = await get_metadata(chat_id, user_id, event, 120, "Send Metadata Title")
                        if metadata:
                            await saveoptions(user_id, 'metadata', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'custom_metadata', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Custom Metadata - {str(new_position)}")
            elif txt.startswith("generaluploadtg"):
                if not eval(new_position):
                    # Highlighted change: Check for Rclone config OR Gofile (no config needed for Gofile yet)
                    current_destination = user_data.get('upload_destination', 'Rclone')
                    if current_destination == 'Rclone' and not (check_config and drive_name):
                        await event.answer(f"❗Rclone destination selected, but no config/account found. Save Rclone Config first.", alert=True)
                        return
                    # No check needed if destination is Gofile
                # End of highlighted change
                await saveoptions(user_id, 'upload_tg', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Upload On TG - {str(new_position)}")
# Highlighted change: Added handler for upload destination & corrected value extraction
            elif txt.startswith(callback_prefix): # Use the defined prefix
                # Correctly extract the value ("Rclone" or "Gofile")
                selected_destination = txt.replace(callback_prefix, "")
                await saveoptions(user_id, 'upload_destination', selected_destination, SAVE_TO_DATABASE)
                await event.answer(f"✅Upload Destination Set To - {str(selected_destination)}")
# End of highlighted change
            elif txt.startswith("generaldrivename"):
                await saveoptions(user_id, 'drive_name', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Rclone Account - {str(new_position)}")
            elif txt.startswith("generalautodrive"):
                if eval(new_position):
                    if not (check_config and drive_name):
                        await event.answer(f"❗First Save Rclone ConfigFile/Account", alert=True)
                        return
                await saveoptions(user_id, 'auto_drive', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Auto Upload Big File To Drive - {str(new_position)}")
            elif txt.startswith("generalgenss"):
                await saveoptions(user_id, 'gen_ss', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Generate Screenshots - {str(new_position)}")
            elif txt.startswith("generalssno"):
                await saveoptions(user_id, 'ss_no', int(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅No Of Screenshots - {str(new_position)}")
            elif txt.startswith("generalgensample"):
                await saveoptions(user_id, 'gen_sample', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Generate Sample Video - {str(new_position)}")
            # REMOVED: Multi-task related settings
            # elif txt.startswith("generaluploadall"):
            #     await saveoptions(user_id, 'upload_all', eval(new_position), SAVE_TO_DATABASE)
            #     await event.answer(f"✅Upload Every Multi Task File - {str(new_position)}")
            # elif txt.startswith("generalmultitasks"):
            #     await saveoptions(user_id, 'multi_tasks', eval(new_position), SAVE_TO_DATABASE)
            #     await event.answer(f"✅Multi Tasks - {str(new_position)}")

            # Use .get() with defaults for all settings
            user_data = get_data().get(user_id, {})
            # REMOVED: Fetching removed settings
            # select_stream = user_data.get('select_stream', False)
            # stream = user_data.get('stream', 'ENG')
            # split_video = user_data.get('split_video', False)
            # split = user_data.get('split', '2GB')
            # custom_thumbnail = user_data.get('custom_thumbnail', False)
            # multi_tasks = user_data.get('multi_tasks', False)
            # upload_all = user_data.get('upload_all', True)
            upload_tg = user_data.get('upload_tg', True)
# Highlighted change: Get upload_destination setting
            upload_destination = user_data.get('upload_destination', 'Rclone')
# End of highlighted change
            custom_metadata = user_data.get('custom_metadata', False)
            drive_name = user_data.get('drive_name', False)
            auto_drive = user_data.get('auto_drive', False)
            gen_ss = user_data.get('gen_ss', False)
            ss_no = user_data.get('ss_no', 5)
            gen_sample = user_data.get('gen_sample', False)

            KeyBoard = []
            # REMOVED: Audio selection buttons
            # KeyBoard.append([Button.inline(f'🥝Auto Select Audio - {str(select_stream)}', 'BashAFK')])
            # for board in gen_keyboard(bool_list, select_stream, "generalselectstream", 2, False):
            #     KeyBoard.append(board)
            # KeyBoard.append([Button.inline(f'🍭Select Audio - {str(stream)}', 'BashAFK')])
            # for board in gen_keyboard(['ENG', 'HIN'], stream, "generalstream", 2, False):
            #     KeyBoard.append(board)
            # REMOVED: Split buttons
            # KeyBoard.append([Button.inline(f'🪓Split Video - {str(split_video)}', 'BashAFK')])
            # for board in gen_keyboard(bool_list, split_video, "generalsplitvideo", 2, False):
            #     KeyBoard.append(board)
            # KeyBoard.append([Button.inline(f'🛢Split Size - {str(split)}', 'BashAFK')])
            # for board in gen_keyboard(['2GB', '4GB'], split, "generalsplit", 2, False):
            #     KeyBoard.append(board)
            # REMOVED: Dynamic thumbnail button
            # KeyBoard.append([Button.inline(f'🖼Dynamic Thumbnail - {str(custom_thumbnail)}', 'BashAFK')])
            # for board in gen_keyboard(bool_list, custom_thumbnail, "generalcustomthumbnail", 2, False):
            #     KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🪀Custom Metadata - {str(custom_metadata)} [Click To See]', 'custom_metedata')])
            for board in gen_keyboard(bool_list, custom_metadata, "generalcustommetadata", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🧵Upload On TG - {str(upload_tg)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, upload_tg, "generaluploadtg", 2, False):
                KeyBoard.append(board)
# Highlighted change: Conditionally add Upload Destination button
            if not upload_tg:
                KeyBoard.append([Button.inline(f'📤Upload Destination - {str(upload_destination)}', 'BashAFK')])
                # Use the defined prefix when generating the keyboard
                for board in gen_keyboard(upload_destination_list, upload_destination, "generalupload_destination", 2, False):
                    KeyBoard.append(board)
                # Conditionally add Rclone account selection only if Rclone is the chosen destination
                if upload_destination == 'Rclone' and check_config:
                    accounts = await get_config(r_config)
                    if accounts:
                        KeyBoard.append([Button.inline(f'🔮Rclone Account - {str(drive_name)}', 'BashAFK')])
                        for board in gen_keyboard(accounts, drive_name, "generaldrivename", 2, False):
                            KeyBoard.append(board)
# End of highlighted change
            KeyBoard.append([Button.inline(f'🕹Auto Upload Big File To Drive - {str(auto_drive)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, auto_drive, "generalautodrive", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📷Generate Screenshots - {str(gen_ss)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, gen_ss, "generalgenss", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🎶No Of Screenshots - {str(ss_no)}', 'BashAFK')])
            for board in gen_keyboard([3,5,7,10], ss_no, "generalssno", 4, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🎞Generate Sample Video - {str(gen_sample)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, gen_sample, "generalgensample", 2, False):
                KeyBoard.append(board)
            # REMOVED: Multi-task buttons
            # KeyBoard.append([Button.inline(f'🛰Multi Tasks - {str(multi_tasks)}', 'BashAFK')])
            # for board in gen_keyboard(bool_list, multi_tasks, "generalmultitasks", 2, False):
            #     KeyBoard.append(board)
            # KeyBoard.append([Button.inline(f'⏹Upload Every Multi Task File - {str(upload_all)}', 'BashAFK')])
            # for board in gen_keyboard(bool_list, upload_all, "generaluploadall", 2, False):
            #     KeyBoard.append(board)
            # Highlighted change: Moved Rclone account selection inside the conditional block above
            # if check_config:
            #     accounts = await get_config(r_config)
            #     if accounts:
            #         KeyBoard.append([Button.inline(f'🔮Rclone Account - {str(drive_name)}', 'BashAFK')])
            #         for board in gen_keyboard(accounts, drive_name, "generaldrivename", 2, False):
            #             KeyBoard.append(board)
            # End of highlighted change
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    await event.edit("⚙ General Settings", buttons=KeyBoard)
                except:
                    pass
            else:
                await TELETHON_CLIENT.send_message(chat_id, "⚙ General Settings", buttons=KeyBoard)
            return

###############------Progress------###############
async def progress_callback(event, txt, user_id):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("progressdetailedprogress"):
                await saveoptions(user_id, 'detailed_messages', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Detailed Messages - {str(new_position)}")
            elif txt.startswith("progressshowstats"):
                await saveoptions(user_id, 'show_stats', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Stats - {str(new_position)}")
            elif txt.startswith("progressupdatetime"):
                await saveoptions(user_id, 'update_time', int(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Progress Update Time - {str(new_position)} secs")
            elif txt.startswith("progressffmpegsize"):
                await saveoptions(user_id, 'ffmpeg_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show FFMPEG Output File Size - {str(new_position)}")
            elif txt.startswith("progressffmpegptime"):
                await saveoptions(user_id, 'ffmpeg_ptime', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Process Time - {str(new_position)}")
            elif txt.startswith("progressshowtime"):
                await saveoptions(user_id, 'show_time', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Show Current Time - {str(new_position)}")

            # Use .get() with defaults
            user_data = get_data().get(user_id, {})
            detailed_messages = user_data.get('detailed_messages', True)
            show_stats = user_data.get('show_stats', True)
            update_time = user_data.get('update_time', 7)
            ffmpeg_size = user_data.get('ffmpeg_size', True)
            ffmpeg_ptime = user_data.get('ffmpeg_ptime', True)
            show_time = user_data.get('show_time', True)

            KeyBoard.append([Button.inline(f'📋Show Detailed Messages - {str(detailed_messages)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, detailed_messages, "progressdetailedprogress", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📊Show Stats - {str(show_stats)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, show_stats, "progressshowstats", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📀Show FFMPEG Output File Size - {str(ffmpeg_size)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, ffmpeg_size, "progressffmpegsize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⏲Show Process Time- {str(ffmpeg_ptime)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, ffmpeg_ptime, "progressffmpegptime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⌚Show Current Time- {str(show_time)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, show_time, "progressshowtime", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⏱Progress Update Time - {str(update_time)} secs', 'BashAFK')])
            for board in gen_keyboard([5, 6, 7, 8, 9, 10], update_time, "progressupdatetime", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            try:
                await event.edit("⚙ Progress Bar Settings", buttons=KeyBoard)
            except:
                pass
            return

# REMOVED: compress_callback function
# ###############------Compress------###############
# async def compress_callback(event, txt, user_id, edit):
#             ... (function content removed) ...

# REMOVED: watermark_callback function
# ###############------Watermark------###############
# async def watermark_callback(event, txt, user_id, edit):
#             ... (function content removed) ...


###############------Merge------###############
async def merge_callback(event, txt, user_id):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("mergemap"):
                await saveconfig(user_id, 'merge', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Merge Map - {str(new_position)}")
            elif txt.startswith("mergefixblank"):
                await saveconfig(user_id, 'merge', 'fix_blank', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Merge Fix Blank - {str(new_position)}")

            # Use .get() with defaults
            merge_settings = get_data().get(user_id, {}).get('merge', {})
            merge_map = merge_settings.get('map', True)
            merge_fix_blank = merge_settings.get('fix_blank', False)

            KeyBoard.append([Button.inline(f'🍓Map  - {str(merge_map)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, merge_map, "mergemap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🚢Fix Blank Outro  - {str(merge_fix_blank)} [Use Only When Necessary]', 'BashAFK')])
            for board in gen_keyboard(bool_list, merge_fix_blank, "mergefixblank", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            try:
                await event.edit("⚙ Merge Settings", buttons=KeyBoard)
            except:
                pass
            return

###############------Convert------###############
async def convert_callback(event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            # Added from VFBITMOD-update
            if txt.startswith("convertencode"):
                await saveconfig(user_id, 'convert', 'encode', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Encode - {str(new_position)}")
            elif txt.startswith("converttype"):
                await saveconfig(user_id, 'convert', 'type', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Encode Type - {str(new_position)}")
            # End of Added from VFBITMOD-update
            elif txt.startswith("convertpreset"):
                await saveconfig(user_id, 'convert', 'preset', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Preset - {str(new_position)}")
            elif txt.startswith("convertcopysub"):
                await saveconfig(user_id, 'convert', 'copy_sub', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Copy Subtitles - {str(new_position)}")
            elif txt.startswith("convertmap"):
                await saveconfig(user_id, 'convert', 'map', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Map - {str(new_position)}")
            elif txt.startswith("convertusequeuesize"):
                await saveconfig(user_id, 'convert', 'use_queue_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Use Queue Size - {str(new_position)}")
            elif txt.startswith("convertsync"):
                await saveconfig(user_id, 'convert', 'sync', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Use SYNC - {str(new_position)}")

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
            KeyBoard.append([Button.inline(f'🎧Encode - {str(convert_encode)}', 'BashAFK')])
            for board in gen_keyboard(encode_list, convert_encode, "convertencode", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🎧Encode Type - {str(convert_type)}', 'BashAFK')])
            # Highlighted change: Updated items per row for type_list
            for board in gen_keyboard(type_list, convert_type, "converttype", 4, False): # Changed items per row to 4 for CBR
                KeyBoard.append(board)
            # End of Added from VFBITMOD-update

            KeyBoard.append([Button.inline(f'🍄Copy Subtitles - {str(convert_copysub)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, convert_copysub, "convertcopysub", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍓Map  - {str(convert_map)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, convert_map, "convertmap", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📻Use FFMPEG Queue Size  - {str(convert_use_queue_size)}', 'BashAFK')])
            if convert_use_queue_size:
                KeyBoard.append([Button.inline(f'🎹FFMPEG Queue Size Value  - {str(convert_queue_size)} (Click To Change)', 'change_convert_queue_size')])
            for board in gen_keyboard(bool_list, convert_use_queue_size, "convertusequeuesize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🌳Use SYNC - {str(convert_sync)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, convert_sync, "convertsync", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'♒Preset - {str(convert_preset)}', 'BashAFK')])
            for board in gen_keyboard(presets_list, convert_preset, "convertpreset", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    await event.edit("⚙ Convert Settings", buttons=KeyBoard)
                except:
                    pass
            else:
                try:
                    await event.delete()
                except:
                    pass
                await Telegram.TELETHON_CLIENT.send_message(event.chat.id, "⚙ Convert Settings", buttons=KeyBoard)
            return

###############------Hardmux------###############
async def hardmux_callback(event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("hardmuxencoder"):
                await saveconfig(user_id, 'hardmux', 'encoder', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Encoder - {str(new_position)}")
            elif txt.startswith("hardmuxencodevideo"):
                await saveconfig(user_id, 'hardmux', 'encode_video', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Use Encoder - {str(new_position)}")
            elif txt.startswith("hardmuxpreset"):
                await saveconfig(user_id, 'hardmux', 'preset', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Preset - {str(new_position)}")
            elif txt.startswith("hardmuxcrf"):
                await saveconfig(user_id, 'hardmux', 'crf', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux CRF - {str(new_position)}")
            elif txt.startswith("hardmuxusequeuesize"):
                await saveconfig(user_id, 'hardmux', 'use_queue_size', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Use Queue Size - {str(new_position)}")
            elif txt.startswith("hardmuxsync"):
                await saveconfig(user_id, 'hardmux', 'sync', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"✅Hardmux Use SYNC - {str(new_position)}")

            # Use .get() with defaults
            hardmux_settings = get_data().get(user_id, {}).get('hardmux', {})
            hardmux_encode_video = hardmux_settings.get('encode_video', True)
            hardmux_encoder = hardmux_settings.get('encoder', 'libx265')
            hardmux_preset = hardmux_settings.get('preset', 'ultrafast')
            hardmux_crf = hardmux_settings.get('crf', '23')
            hardmux_use_queue_size = hardmux_settings.get('use_queue_size', False)
            hardmux_queue_size = hardmux_settings.get('queue_size', '9999')
            hardmux_sync = hardmux_settings.get('sync', False)

            KeyBoard.append([Button.inline(f'🎧Use Encoder - {str(hardmux_encode_video)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, hardmux_encode_video, "hardmuxencodevideo", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🍬Encoder - {str(hardmux_encoder)}', 'BashAFK')])
            for board in gen_keyboard(encoders_list, hardmux_encoder, "hardmuxencoder", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'📻Use FFMPEG Queue Size  - {str(hardmux_use_queue_size)}', 'BashAFK')])
            if hardmux_use_queue_size:
                KeyBoard.append([Button.inline(f'🎹FFMPEG Queue Size Value  - {str(hardmux_queue_size)} (Click To Change)', 'change_hardmux_queue_size')])
            for board in gen_keyboard(bool_list, hardmux_use_queue_size, "hardmuxusequeuesize", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🌳Use SYNC - {str(hardmux_sync)}', 'BashAFK')])
            for board in gen_keyboard(bool_list, hardmux_sync, "hardmuxsync", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'♒Preset - {str(hardmux_preset)}', 'BashAFK')])
            for board in gen_keyboard(presets_list, hardmux_preset, "hardmuxpreset", 3, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'⚡CRF  - {str(hardmux_crf)}', 'BashAFK')])
            for board in gen_keyboard(crf_list, hardmux_crf, "hardmuxcrf", 6, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    await event.edit("⚙ Hardmux Settings", buttons=KeyBoard)
                except:
                    pass
            else:
                try:
                    await event.delete()
                except:
                    pass
                await Telegram.TELETHON_CLIENT.send_message(event.chat.id, "⚙ Hardmux Settings", buttons=KeyBoard)
            return


###############------Softmux------###############
async def softmux_callback(event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("softmuxsubcodec"):
                await saveconfig(user_id, 'softmux', 'sub_codec', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Softmux Sub Codec - {str(new_position)}")

            # Use .get() with defaults
            softmux_settings = get_data().get(user_id, {}).get('softmux', {})
            softmux_sub_codec = softmux_settings.get('sub_codec', 'copy')

            KeyBoard.append([Button.inline(f'🍄Subtitles Codec - {str(softmux_sub_codec)}', 'BashAFK')])
            for board in gen_keyboard(['copy', 'mov_text'], softmux_sub_codec, "softmuxsubcodec", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    await event.edit("⚙ Softmux Settings", buttons=KeyBoard)
                except:
                    pass
            else:
                try:
                    await event.delete()
                except:
                    pass
                await Telegram.TELETHON_CLIENT.send_message(event.chat.id, "⚙ Softmux Settings", buttons=KeyBoard)
            return

# REMOVED: softremux_callback function
# ###############------Softremux------###############
# async def softremux_callback(event, txt, user_id, edit):
#             ... (function content removed) ...

# Added from VFBITMOD-update
###############------Video------###############
async def video_callback(event, txt, user_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("videoencude"):
                await saveconfig(user_id, 'video', 'encude', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅FOrmant - {str(new_position)}")
            elif txt.startswith("videovbit"):
                await saveconfig(user_id, 'video', 'vbit', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert VideoBit - {str(new_position)}")
            elif txt.startswith("videoquality"):
                await saveconfig(user_id, 'video', 'qubality', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Quality - {str(new_position)}")
# Highlighted change: Added tune callback handler
            elif txt.startswith("videotune"):
                await saveconfig(user_id, 'video', 'tune', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Video Tune - {str(new_position)}")
# End of highlighted change
# Highlighted change: Added processing unit callback handler
            elif txt.startswith("videoprocessing_unit"):
                await saveoptions(user_id, 'processing_unit', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Processing Unit - {str(new_position)}")
# End of highlighted change

            # Use .get() with defaults
            user_data = get_data().get(user_id, {}) # Get user_data once
            video_settings = user_data.get('video', {})
            video_vbit = video_settings.get('vbit', '8Bit')
            video_encude = video_settings.get('encude', 'HEVC')
            video_qubality = video_settings.get('qubality', '480p [720x480]')
# Highlighted change: Get tune setting
            video_tune = video_settings.get('tune', 'None')
# End of highlighted change
# Highlighted change: Get processing unit setting
            processing_unit = user_data.get('processing_unit', 'CPU')
# End of highlighted change

            KeyBoard.append([Button.inline(f'❤ Encoder - {str(video_encude)}', 'BashAFK')])
            for board in gen_keyboard(encude_list, video_encude, "videoencude", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'❤ VideoBit - {str(video_vbit)}', 'BashAFK')])
            for board in gen_keyboard(vbit_list, video_vbit, "videovbit", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'❤ Resolution - {str(video_qubality)}', 'BashAFK')])
            for board in gen_keyboard(qubality_list, video_qubality, "videoquality", 2, False):
                KeyBoard.append(board)
# Highlighted change: Added tune buttons
            KeyBoard.append([Button.inline(f'❤ Tune - {str(video_tune)}', 'BashAFK')])
            for board in gen_keyboard(tune_list, video_tune, "videotune", 3, False): # Display 3 tune options per row
                KeyBoard.append(board)
# End of highlighted change
# Highlighted change: Added processing unit buttons
            KeyBoard.append([Button.inline(f'❤ Processing Unit - {str(processing_unit)}', 'BashAFK')])
            for board in gen_keyboard(processing_unit_list, processing_unit, "videoprocessing_unit", 2, False):
                KeyBoard.append(board)
# End of highlighted change

            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    await event.edit("🎬 Video Settings", buttons=KeyBoard)
                except:
                    pass
            else:
                try:
                    await event.delete()
                except:
                    pass
                await Telegram.TELETHON_CLIENT.send_message(event.chat.id, "🎬 Video Settings", buttons=KeyBoard)
            return

###############-----Audio------###############
async def audio_callback(event, txt, user_id, chat_id, edit):
            new_position = txt.split("_", 1)[1]
            KeyBoard = []
            if txt.startswith("audioachannel"):
                await saveconfig(user_id, 'audio', 'achannel', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Audio Channel - {str(new_position)}")
            elif txt.startswith("audioacodec"):
                await saveconfig(user_id, 'audio', 'acodec', new_position, SAVE_TO_DATABASE)
                await event.answer(f"✅Convert Audio codec - {str(new_position)}")
            elif txt.startswith("audioabit"):
                if eval(new_position):
                        metadata = await get_abit(chat_id, user_id, event, 120, "**Send AudioBit Value\n\n****Example :** `128k`, `760k` etc.")
                        if metadata:
                            await saveoptions(user_id, 'abit', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_abit', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ AudioBit 🖤 - {str(new_position)}")

            # Use .get() with defaults
            user_data = get_data().get(user_id, {})
            audio_settings = user_data.get('audio', {})
            use_abit = user_data.get('use_abit', False)
            audio_acodec = audio_settings.get('acodec', 'AAC')
            audio_achannel = audio_settings.get('achannel', '2')

            KeyBoard.append([Button.inline(f'🖤 Audio Codec - {str(audio_acodec)}', 'BashAFK')])
            for board in gen_keyboard(acodec_list, audio_acodec, "audioacodec", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🖤 Audio Channel - {str(audio_achannel)}', 'BashAFK')])
            for board in gen_keyboard(achannel_list, audio_achannel, "audioachannel", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🖤 AudioBit - {str(use_abit)} [Click To See]', 'abit_value')])
            for board in gen_keyboard(bool_list, use_abit, "audioabit", 2, False):
                KeyBoard.append(board)

            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    await event.edit("🔊 Audio Settings", buttons=KeyBoard)
                except:
                    pass
            else:
                try:
                    await event.delete()
                except:
                    pass
                await Telegram.TELETHON_CLIENT.send_message(event.chat.id, "🔊 Audio Settings", buttons=KeyBoard)
            return

###############-----CRF By Word------###############
async def vbrcrf_callback(event, txt, user_id, chat_id):
            new_position = txt.split("_", 1)[1]
            edit = True
            if txt.startswith("vbrcrfvbr"):
                if eval(new_position):
                        metadata = await get_vbr(chat_id, user_id, event, 120, "**Send VBR Value**\n\n**Example :** `400k`, `900k` etc.")
                        if metadata:
                            await saveoptions(user_id, 'vbr', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_vbr', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ VBR 🖤 - {str(new_position)}")
            elif txt.startswith("vbrcrfcrf"):
                if eval(new_position):
                        metadata = await get_crf(chat_id, user_id, event, 120, "**Send CRF Value**\n\n**Example :** `22`, `28` etc.")
                        if metadata:
                            await saveoptions(user_id, 'crf', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_crf', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ CRF 🖤 - {str(new_position)}")
            # Added ABR handling
            elif txt.startswith("vbrcrfabr"):
                if eval(new_position):
                        metadata = await get_abr(chat_id, user_id, event, 120, "**Send ABR Value**\n\n**Example :** `1500k`, `2M` etc.")
                        if metadata:
                            await saveoptions(user_id, 'abr', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_abr', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ ABR 🖤 - {str(new_position)}")
            # Highlighted change: Added CBR handling
            elif txt.startswith("vbrcrfcbr"):
                if eval(new_position):
                        metadata = await get_cbr(chat_id, user_id, event, 120, "**Send CBR Value**\n\n**Example :** `1500k`, `2M` etc.")
                        if metadata:
                            await saveoptions(user_id, 'cbr', metadata, SAVE_TO_DATABASE)
                            edit = False
                        else:
                            return
                await saveoptions(user_id, 'use_cbr', eval(new_position), SAVE_TO_DATABASE)
                await event.answer(f"❤ CBR 🖤 - {str(new_position)}")

            # Use .get() with defaults
            user_data = get_data().get(user_id, {})
            use_vbr = user_data.get('use_vbr', False)
            use_crf = user_data.get('use_crf', False)
            use_abr = user_data.get('use_abr', False) # Get ABR setting
            # Highlighted change: Get CBR setting
            use_cbr = user_data.get('use_cbr', False) # Get CBR setting

            KeyBoard = []
            KeyBoard.append([Button.inline(f'❤ VBR - {str(use_vbr)} [Click To See]', 'vbr_value')])
            for board in gen_keyboard(bool_list, use_vbr, "vbrcrfvbr", 2, False):
                KeyBoard.append(board)
            KeyBoard.append([Button.inline(f'🖤 CRF - {str(use_crf)} [Click To See]', 'crf_value')])
            for board in gen_keyboard(bool_list, use_crf, "vbrcrfcrf", 2, False):
                KeyBoard.append(board)
            # Added ABR button row
            KeyBoard.append([Button.inline(f'💙 ABR - {str(use_abr)} [Click To See]', 'abr_value')])
            for board in gen_keyboard(bool_list, use_abr, "vbrcrfabr", 2, False):
                KeyBoard.append(board)
            # Highlighted change: Added CBR button row
            KeyBoard.append([Button.inline(f'💚 CBR - {str(use_cbr)} [Click To See]', 'cbr_value')])
            for board in gen_keyboard(bool_list, use_cbr, "vbrcrfcbr", 2, False):
                KeyBoard.append(board)

            KeyBoard.append([Button.inline(f'↩Back', 'settings')])
            if edit:
                try:
                    # Highlighted change: Updated title
                    await event.edit("❤ Rate Control (VBR/CRF/ABR/CBR) Settings", buttons=KeyBoard) # Modified title
                except:
                    pass
            else:
                # Highlighted change: Updated title
                await TELETHON_CLIENT.send_message(chat_id, "❤ Rate Control (VBR/CRF/ABR/CBR) Settings", buttons=KeyBoard) # Modified title
            return
# End of Added from VFBITMOD-update

# --- END OF FILE VideoFlux-Re-master/bot/callbacks.py ---
