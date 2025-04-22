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
# REMOVED: Telethon imports
# from telethon.functions import bots
# from telethon.types import BotCommand, BotCommandScopeDefault
# ADDED: Pyrogram idle import
from pyrogram import idle


#////////////////////////////////////Variables////////////////////////////////////#
working_dir = "./bot"
files = glob(f'{working_dir}/*.py')
DATA = Config.DATA
sudo_users = Config.SUDO_USERS
LOGGER = Config.LOGGER

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
# MODIFIED: Use Pyrogram client
async def get_me(client):
    return await client.get_me()


# REMOVED: set_bot_commands function (used Telethon)
# ###############------Set_Bot_Commands-----###############
# async def set_bot_commands(command_file):
#         ... (function content removed) ...


###############------Check_Restart------###############
# MODIFIED: Use Pyrogram client
async def check_restart(restart_file):
    try:
        with open(restart_file) as f:
            chat, msg_id = map(int, f)
        remove(restart_file)
        # Use Pyrogram client to edit message
        await Telegram.PYROGRAM_CLIENT.edit_message_text(chat, msg_id, '✅Restarted Successfully')
    except Exception as e:
        LOGGER.info("🧩Error While Updating Restart Message:\n\n", e)
    return

# REMOVED: start_user_account function (used Telethon)
# ###############------Start_User_Session------###############
# def start_user_account():
#     ... (function content removed) ...

###############------Restart_Notification------###############
# MODIFIED: Use Pyrogram client
async def notify_restart(RESTART_NOTIFY_ID):
    try:
        await Telegram.PYROGRAM_CLIENT.send_message(RESTART_NOTIFY_ID, "⚡Bot Started Successfully⚡")
    except Exception as e:
        LOGGER.info("❗Failed To Send Restart Notification ", e)
    return


if __name__ == "__main__":
    # REMOVED: Telethon client startup
    # LOGGER.info("🔶Starting Telethon Bot")
    # Telegram.TELETHON_CLIENT.start(bot_token=Config.TOKEN)
    # telethob_bot = Telegram.TELETHON_CLIENT.loop.run_until_complete(get_me(Telegram.TELETHON_CLIENT))

    # MODIFIED: Check restart using Pyrogram client's loop
    LOGGER.info("🔶Checking For Restart Notification")
    if exists(".restartmsg"):
        # Run async check_restart within Pyrogram's loop context if possible,
        # or handle it before starting the main Pyrogram loop if necessary.
        # For simplicity here, we assume it can run before idle.
        # A more robust solution might involve running it after client start.
        try:
             Telegram.PYROGRAM_CLIENT.loop.run_until_complete(check_restart(".restartmsg"))
        except Exception as e:
             LOGGER.error(f"Error running check_restart in loop: {e}")
             # Attempt direct call if loop isn't ready (less ideal)
             # asyncio.run(check_restart(".restartmsg")) # Requires asyncio import
    elif Config.RESTART_NOTIFY_ID:
         try:
            Telegram.PYROGRAM_CLIENT.loop.run_until_complete(notify_restart(Config.RESTART_NOTIFY_ID))
         except Exception as e:
             LOGGER.error(f"Error running notify_restart in loop: {e}")
             # asyncio.run(notify_restart(Config.RESTART_NOTIFY_ID)) # Requires asyncio import


    if Config.USE_PYROGRAM:
        LOGGER.info("🔶Starting Pyrogram Bot")
        Telegram.PYROGRAM_CLIENT.start() # Start Pyrogram client
        pyrogram_bot = Telegram.PYROGRAM_CLIENT.get_me() # Get bot info after start
        LOGGER.info(f'✅Pyrogram Session For @{pyrogram_bot.username} Started Successfully!✅')
    else:
        # This case should ideally not happen if we're standardizing on Pyrogram
        LOGGER.warning("🔶USE_PYROGRAM is False, but Telethon support is removed. Bot might not function.")

    # REMOVED: Telethon user client startup
    # if Telegram.TELETHON_USER_CLIENT:
    #     start_user_account()
    # else:
    #     LOGGER.info("🔶Not Starting User Session")

    start_listener() # Start Aria2 listener

    # REMOVED: Telethon bot command setting
    # if exists("commands.txt") and Config.AUTO_SET_BOT_CMDS:
    #     Telegram.TELETHON_CLIENT.loop.run_until_complete(set_bot_commands("commands.txt"))
    # else:
    #     LOGGER.info("🔶Not Setting Up Bot Commands")

    # MODIFIED: Log Pyrogram bot username
    LOGGER.info(f'✅@{pyrogram_bot.username} Started Successfully!✅')
    LOGGER.info(f"⚡Bot By Sahil Nolia⚡")
    # REMOVED: Telethon run_until_disconnected
    # Telegram.TELETHON_CLIENT.run_until_disconnected()
    # ADDED: Pyrogram idle loop
    idle()
    LOGGER.info("🛑 Bot Stopped")
    Telegram.PYROGRAM_CLIENT.stop() # Stop Pyrogram client on exit

# --- END OF FILE VideoFlux-Re-master/main.py ---
