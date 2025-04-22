# --- START OF FILE VideoFlux-Re-master/main.py ---

from config.config import Config
from sys import modules
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from glob import glob
from bot_helper.Aria2.Aria2_Engine import start_listener
from bot_helper.Telegram.Telegram_Client import Telegram
from os.path import exists
from os import remove
from telethon.functions import bots
from telethon.types import BotCommand, BotCommandScopeDefault


#////////////////////////////////////Variables////////////////////////////////////#
working_dir = "./bot"
files = glob(f'{working_dir}/*.py')
DATA = Config.DATA
sudo_users = Config.SUDO_USERS
LOGGER = Config.LOGGER
# Highlighted change: Define Pyrogram session name
PYROGRAM_SESSION_NAME = f"Pyrogram_{Config.NAME}.session"

###############------Load_Plugins------###############
def load_plugins(plugin_name):
    path = Path(f"{working_dir}/{plugin_name}.py")
    name = "main.plugins.{}".format(plugin_name)
    spec = spec_from_file_location(name, path)
    load = module_from_spec(spec)
    spec.loader.exec_module(load)
    modules["main.plugins." + plugin_name] = load
    LOGGER.info("🔷Successfully Imported " + plugin_name)
    return

###############------Get_Plugins------###############
for name in files:
    with open(name) as a:
        patt = Path(a.name)
        plugin_name = patt.stem
        load_plugins(plugin_name.replace(".py", ""))

###############------Get_Client_Details-----###############
async def get_me(client):
    return await client.get_me()


###############------Set_Bot_Commands-----###############
async def set_bot_commands(command_file):
        LOGGER.info("🔶Setting Up Bot Commands")
        try:
                commands = []
                with open(command_file, "r", encoding="utf-8") as f:
                    # Highlighted change: Process lines one by one with checks
                    for line in f:
                        cleaned_line = line.strip()
                        # Skip empty lines and comments
                        if not cleaned_line or cleaned_line.startswith("#"):
                            continue
                        # Split the valid line
                        parts = cleaned_line.split("-", 1) # Split only once
                        # Ensure we got exactly two parts after splitting
                        if len(parts) == 2:
                            command_text = parts[0].strip()
                            description_text = parts[1].strip()
                            # Ensure command is not empty after stripping
                            if command_text:
                                commands.append(BotCommand(
                                    command=command_text,
                                    description=description_text
                                ))
                        else:
                            LOGGER.warning(f"Skipping malformed line in {command_file}: {cleaned_line}")
                    # End of highlighted change

                # Check if any valid commands were found
                if commands:
                    result = await Telegram.TELETHON_CLIENT(bots.SetBotCommandsRequest(
                                                scope=BotCommandScopeDefault(),
                                                lang_code='en',
                                                commands=commands
                                            ))
                    LOGGER.info(f"🔶Commands Setup Result: {str(result)}")
                else:
                    LOGGER.warning(f"No valid commands found in {command_file} to set.")

        except Exception as e:
                # Log the exception with traceback for better debugging if needed
                LOGGER.exception(f"❗Failed To Setup Bot Commands: {str(e)}")
        return


###############------Check_Restart------###############
async def check_restart(restart_file):
    try:
        with open(restart_file) as f:
            chat, msg_id = map(int, f)
        remove(restart_file)
        await Telegram.TELETHON_CLIENT.edit_message(chat, msg_id, '✅Restarted Successfully')
    except Exception as e:
        LOGGER.info("🧩Error While Updating Restart Message:\n\n", e)
    return

###############------Start_User_Session------###############
def start_user_account():
    Telegram.TELETHON_USER_CLIENT.start()
    user = Telegram.TELETHON_CLIENT.loop.run_until_complete(get_me(Telegram.TELETHON_USER_CLIENT))
    first_name = user.first_name
    if not user.premium:
        LOGGER.info(f"⛔User Account {first_name} Don't Have Telegram Premium, 2GB Limit Will Be Used For Telegram Uploading.")
    else:
        LOGGER.info(f"💎Telegram Premium Found For  User {first_name}")
    LOGGER.info(f'🔒Session For {first_name} Started Successfully!🔒')
    return

###############------Restart_Notification------###############
async def notify_restart(RESTART_NOTIFY_ID):
    try:
        await Telegram.TELETHON_CLIENT.send_message(RESTART_NOTIFY_ID, "⚡Bot Started Successfully⚡")
    except Exception as e:
        LOGGER.info("❗Failed To Send Restart Notification ", e)
    return


if __name__ == "__main__":
    LOGGER.info("🔶Starting Telethon Bot")
    Telegram.TELETHON_CLIENT.start(bot_token=Config.TOKEN)
    telethob_bot = Telegram.TELETHON_CLIENT.loop.run_until_complete(get_me(Telegram.TELETHON_CLIENT))
    LOGGER.info("🔶Checking For Restart Notification")
    if exists(".restartmsg"):
        Telegram.TELETHON_CLIENT.loop.run_until_complete(check_restart(".restartmsg"))
    elif Config.RESTART_NOTIFY_ID:
        Telegram.TELETHON_CLIENT.loop.run_until_complete(notify_restart(Config.RESTART_NOTIFY_ID))
    if Config.USE_PYROGRAM:
        # Highlighted change: Delete existing Pyrogram session file before starting
        if exists(PYROGRAM_SESSION_NAME):
            try:
                remove(PYROGRAM_SESSION_NAME)
                LOGGER.info(f"🔶Deleted existing Pyrogram session file: {PYROGRAM_SESSION_NAME}")
            except Exception as e:
                LOGGER.error(f"❗Failed to delete Pyrogram session file {PYROGRAM_SESSION_NAME}: {e}")
        # End of highlighted change
        LOGGER.info("🔶Starting Pyrogram Bot")
        pyrogram_bot = Telegram.PYROGRAM_CLIENT.start()
        LOGGER.info(f'✅Pyrogram Session For @{pyrogram_bot.get_me().username} Started Successfully!✅')
    else:
        LOGGER.info("🔶Not Starting Pyrogram bot")
    if Telegram.TELETHON_USER_CLIENT:
        start_user_account()
    else:
        LOGGER.info("🔶Not Starting User Session")
    start_listener()
    if exists("commands.txt") and Config.AUTO_SET_BOT_CMDS:
        Telegram.TELETHON_CLIENT.loop.run_until_complete(set_bot_commands("commands.txt"))
    else:
        LOGGER.info("🔶Not Setting Up Bot Commands")
    LOGGER.info(f'✅@{telethob_bot.username} Started Successfully!✅')
    LOGGER.info(f"⚡Bot By Sahil Nolia⚡")
    Telegram.TELETHON_CLIENT.run_until_disconnected()

# --- END OF FILE VideoFlux-Re-master/main.py ---
