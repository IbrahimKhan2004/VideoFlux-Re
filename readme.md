# VideoFlux-Re-master Bot

A multi-feature Telegram bot for video processing tasks like merging, converting, muxing, generating samples/screenshots, and uploading.

## Features

*   **Merge:** Combine multiple video files into one.
*   **Convert:** Encode videos to different formats (H.264, HEVC, VP9, **<ins>AV1</ins>**), resolutions, bit depths, and apply various rate control methods.
*   **HardMux:** Burn subtitles directly into the video stream.
*   **SoftMux:** Add subtitles as separate selectable tracks within the video container.
*   **Metadata/Index Manipulation:**
    *   Change audio/subtitle track metadata (language, title).
    *   Reorder audio/subtitle tracks.
*   **Utilities:**
    *   Generate video sample clips.
    *   Generate video screenshots.
*   **Upload:**
    *   Upload processed files to Telegram.
    *   Optionally upload to Rclone remotes or Gofile.io if Telegram upload is disabled.
*   **Configuration:** Highly configurable via bot settings and environment variables.
*   **Status Tracking:** Detailed progress updates for ongoing tasks.

## Configuration

Set up the bot using environment variables. You can create a `config.env` file in the root directory or set the environment variables directly. Alternatively, provide a direct URL to your `config.env` file via the `CONFIG_FILE_URL` environment variable.

**Required Variables:**

*   `API_ID`: Your Telegram API ID from [my.telegram.org](https://my.telegram.org).
*   `API_HASH`: Your Telegram API Hash from [my.telegram.org](https://my.telegram.org).
*   `TOKEN`: Your Telegram Bot Token from [@BotFather](https://t.me/BotFather).
*   `OWNER_ID`: The numerical Telegram User ID of the bot owner.
*   `SUDO_USERS`: Space-separated list of numerical Telegram User IDs for sudo users.
*   `RUNNING_TASK_LIMIT`: Maximum number of concurrent tasks the bot can handle (e.g., `2`).
*   `FINISHED_PROGRESS_STR`: Character(s) for the filled part of the progress bar (e.g., `■`).
*   `UNFINISHED_PROGRESS_STR`: Character(s) for the empty part of the progress bar (e.g., `□`).
*   `AUTO_SET_BOT_CMDS`: Set to `True` to automatically set bot commands on startup, `False` otherwise.
*   `SAVE_TO_DATABASE`: Set to `True` to save user settings to MongoDB, `False` to keep settings in memory only (lost on restart).
*   `Use_Session_String`: Set to `True` if you want to use a Telethon User Session String for potentially faster uploads or >2GB uploads (requires premium), `False` otherwise.

**Optional Variables:**

*   `AUTH_GROUP_ID`: Numerical chat ID of a group where the bot has admin rights (needed for Pyrogram file operations in groups if used).
*   `RESTART_NOTIFY_ID`: User or Chat ID to send a notification to when the bot restarts.
*   `UPSTREAM_REPO`: Your GitHub repository URL for updates (e.g., `https://github.com/user/repo`). For private repos use `https://username:token@github.com/user/repo`.
*   `UPSTREAM_BRANCH`: The branch to pull updates from (default: `master`).
*   `TIMEZONE`: Timezone for status messages (default: `Asia/Kolkata`). List [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
*   `MONGODB_URI`: Your MongoDB connection string (Required if `SAVE_TO_DATABASE` is `True`).
*   `Session_String`: Your Telethon Session String (Required if `Use_Session_String` is `True`).

## Commands

Here's a list of available commands:

*   `/merge`: Merge multiple videos.
*   `/convert`: Convert a video (change codec, resolution, rate control, etc.).
*   `/hardmux`: Burn a subtitle file into a video.
*   `/softmux`: Add subtitle files as tracks to a video.
*   `/gensample`: Generate a short sample clip from a video.
*   `/genss`: Generate screenshots from a video.
*   `/changemetadata`: Modify metadata (language, title) of audio/subtitle tracks.
*   `/changeindex`: Reorder audio/subtitle tracks or remove streams.
*   `/savethumb`: Save a static thumbnail image to be used for uploads.
*   `/saveconfig`: Save/replace your Rclone configuration file (`rclone.conf`).
*   `/tasklimit` (Owner only): Change the bot's concurrent task limit.
*   `/status`: Show the status of ongoing and queued tasks.
*   `/cancel <aria|process> <id>`: Cancel a specific download (aria) or processing (process) task.
*   `/ffmpeg log <process_id>`: Get the FFMPEG log file for a specific completed/failed process.
*   `/log` (Sudo only): Get the last few lines of the bot's main log.
*   `/logs` (Sudo only): Get the full bot's main log file (`Logging.txt`).
*   `/renew` (Owner only): Clear the `downloads` directory.
*   `/resetdb` (Owner only): Reset all user settings (use with caution!).
*   `/changeconfig` (Owner only): Interactively change bot config variables (from `.env` file).
*   `/clearconfigs` (Owner only): Delete the custom `botconfig.env` and revert to default environment variables on next restart.
*   `/addsudo <user_id|reply>` (Owner only): Add a user to the sudo list.
*   `/delsudo <user_id|reply>` (Owner only): Remove a user from the sudo list.
*   `/checksudo` (Owner only): List current sudo users.
*   `/time` (Sudo only): Show the bot's uptime.
*   `/stats` (Sudo only): Show detailed host system stats.
*   `/speedtest` (Sudo only): Run a network speed test.
*   `/settings`: Access the user settings menu.
*   `/start`: Start command and basic info.
*   `/restart` (Owner only): Restart the bot.

*(Note: Some commands related to Compression, Watermark, SoftReMux, Leech, Mirror, and Heroku have been removed as the corresponding features are no longer present in this version).*

## Encoding & Rate Control Guide

You can configure encoding options via `/settings`.

### Encoder Choice (`/settings` -> `Video`)

*   **HEVC (libx265):** Good compression efficiency, widely supported on modern devices.
*   **H.264 (libx264):** Very compatible, good quality, slightly less efficient than HEVC.
*   **VP9 (libvpx-vp9):** Open source, good compression, well-suited for web streaming.
*   **<ins>AV1 (libsvtav1):</ins>** <ins>Newer open source codec, potentially better compression than HEVC/VP9 at lower bitrates. Encoding can be slower than libx265 but faster than libaom-av1. Requires newer hardware/software for playback.</ins>

### Rate Control (`/settings` -> `Rate Control (VBR/CRF/ABR/CBR)`)

Rate control determines how the encoder allocates bitrate to maintain quality or file size targets.

*   **CRF (Constant Rate Factor):**
    *   **Goal:** Achieve a consistent *perceptual quality* level throughout the video. Bitrate varies based on scene complexity.
    *   **How:** You set a CRF value (e.g., 18-28 for H.264/HEVC, 15-35 for VP9, **<ins>25-40 for AV1</ins>**). Lower values = higher quality = larger file size.
    *   **When:** Best for archiving or when target quality is more important than exact file size.
    *   **VP9 Specific:** When using CRF with VP9, the bot automatically adds `-b:v 0` to the FFmpeg command, which is required.
    *   **<ins>AV1 Specific:</ins>** <ins>CRF is a good option for AV1 quality control.</ins>
    *   **Bot Setting:** Enable `Use CRF` and set the desired `CRF` value.

*   **VBR (Variable Bitrate):**
    *   **Goal:** Target an *average* bitrate for the entire file. Allows bitrate to fluctuate based on complexity but tries to hit the overall target. Often used in 2-pass encoding for better results, but this bot uses 1-pass.
    *   **How:** You specify a target average bitrate (e.g., `1500k`, `2M`).
    *   **When:** When you need to roughly control the file size while still allowing quality variation.
    *   **Bot Setting:** Enable `Use VBR` and set the desired `VBR` value (e.g., `2500k`).

*   **ABR (Average Bitrate):**
    *   **Goal:** Similar to VBR in a 1-pass context, aiming for a target average bitrate. FFmpeg tries its best to match the target rate.
    *   **How:** Specify the target average bitrate (e.g., `1500k`, `2M`).
    *   **When:** Similar use case to 1-pass VBR.
    *   **Bot Setting:** Enable `Use ABR` and set the desired `ABR` value (e.g., `1800k`).

*   **CBR (Constant Bitrate):**
    *   **Goal:** Keep the bitrate as constant as possible throughout the video.
    *   **How:** Set a target bitrate. FFmpeg tries to strictly adhere to this rate, often requiring `-minrate` and `-maxrate` to be set to the same value, along with an appropriate `-bufsize`.
    *   **When:** Sometimes required for specific streaming protocols or hardware, but often less efficient quality-wise compared to CRF/VBR.
    *   **VP9/AV1 Specific:** Achieving *true* CBR with 1-pass VP9/AV1 is difficult and not recommended. **<ins>This bot disables the CBR option when VP9 or AV1 is selected as the encoder.</ins>**
    *   **Bot Setting:** Enable `Use CBR` and set the desired `CBR` value (e.g., `1500k`). (Only available for H.264/HEVC).

**Which Rate Control Type to Choose in Settings?** (`/settings` -> `Convert` -> `Encode Type`)

This setting tells the bot *which* of the enabled rate control values (CRF, VBR, ABR, or CBR) to actually *use* for the `/convert` command.

1.  Go to `/settings` -> `Rate Control`.
2.  Enable *one* of the `Use CRF`, `Use VBR`, `Use ABR`, or `Use CBR` options (remember CBR is unavailable for VP9/AV1).
3.  Set the corresponding value (CRF number, or bitrate like `2000k`).
4.  Go to `/settings` -> `Convert`.
5.  Select the `Encode Type` that matches the rate control you enabled (CRF, VBR, ABR, or CBR).

**Example:** To use CRF 30 for AV1 conversion:
1.  `/settings` -> `Rate Control` -> Enable `Use CRF` -> Set `CRF` to `30`. Ensure other `Use...` options are off.
2.  `/settings` -> `Convert` -> Select `Encode Type` -> `CRF`.
3.  `/settings` -> `Video` -> Select `Encoder` -> `AV1`.

### Encoder Specific Settings (`/settings` -> `Video`)

*   **VP9 Presets:** VP9 doesn't use presets like H.264/HEVC. Instead, it uses `-cpu-used`. The bot maps the familiar preset names to `-cpu-used` values:
    *   `ultrafast`: `-cpu-used 5` (Fastest, lowest quality)
    *   `superfast`: `-cpu-used 4`
    *   `veryfast`: `-cpu-used 3`
    *   `faster`: `-cpu-used 2`
    *   `fast`: `-cpu-used 1`
    *   `medium`, `slow`, `slower`, `veryslow`: `-cpu-used 0` (Slowest, highest quality potential for a given rate control)
    The bot also uses `-deadline good` for 1-pass encodes.

*   **<ins>AV1 Presets (SVT-AV1):</ins>** <ins>The SVT-AV1 encoder uses numerical presets (0-13). Lower numbers mean slower encoding but better quality/efficiency. Higher numbers are faster but offer less quality/efficiency. The bot maps the text presets to these numbers internally:</ins>
    *   <ins>`ultrafast`: `-preset 12`</ins>
    *   <ins>`superfast`: `-preset 10`</ins>
    *   <ins>`veryfast`: `-preset 8`</ins>
    *   <ins>`faster`: `-preset 7`</ins>
    *   <ins>`fast`: `-preset 6`</ins>
    *   <ins>`medium`: `-preset 5` (Good balance)</ins>
    *   <ins>`slow`: `-preset 4`</ins>
    *   <ins>`slower`: `-preset 3`</ins>
    *   <ins>`veryslow`: `-preset 2`</ins>
    <ins>(Note: The bot uses preset 6 as a fallback if an invalid preset name is somehow selected).</ins>

*   **Tune:** The `-tune` parameter (like `film`, `animation`) is generally *not* applicable to VP9 or AV1 (SVT-AV1). **<ins>The Tune option in the bot settings is hidden when VP9 or AV1 is selected.</ins>**

### Other Video Settings (`/settings` -> `Video`)

*   **Resolution:** Choose the desired output resolution (e.g., `720p [1280x720]`).
*   **VideoBit (Bit Depth):** Choose `8Bit` or `10Bit` (10-bit often provides better quality and compression but might have compatibility issues with older devices. AV1 often performs well in 10-bit).

### Other Audio Settings (`/settings` -> `Audio`)

*   **Audio Codec:** Choose AAC, OPUS, AC3 (DD), E-AC3 (DDP).
*   **Audio Channel:** Set to 2 (Stereo) or 6 (5.1 Surround).
*   **AudioBit:** Enable and set a custom audio bitrate (e.g., `128k`, `320k`) if desired.

## Deployment

### Docker

1.  Build the Docker image:
    ```bash
    docker build -t videoflux-bot .
    ```
    *(Ensure the Dockerfile successfully installs an FFmpeg version with libsvtav1 support. See the Dockerfile comments for potential methods like using deb-multimedia).*
2.  Run the container:
    ```bash
    docker run -d --name videoflux --restart always -v $(pwd)/userdata:/app/userdata -v $(pwd)/downloads:/app/downloads --env-file config.env videoflux-bot
    ```
    *(Make sure `config.env` exists or set environment variables directly using `-e KEY=VALUE`)*
    *(Mounting `userdata` preserves settings and Rclone configs across restarts. Mounting `downloads` can be useful but isn't strictly necessary unless you need access outside the container).*

### Docker Compose

1.  Make sure you have `docker-compose` installed.
2.  Create or verify your `config.env` file.
3.  Run:
    ```bash
    docker-compose up -d --build
    ```
    *(This uses the provided `docker-compose.yml` which mounts the current directory. Adjust volumes as needed. Ensure the Dockerfile builds successfully with AV1 support).*

### Manual (Not Recommended for Production)

1.  Install Python 3.9+.
2.  Install dependencies: `apt update && apt install -y ffmpeg wget unzip p7zip-full curl busybox aria2 git` *(Ensure your system's FFmpeg includes libsvtav1 support. You might need to add a PPA or compile from source).*
3.  Install Rclone: `bash <(wget -qO- https://rclone.org/install.sh)`
4.  Install Python packages: `pip3 install --no-cache-dir -r requirements.txt`
5.  Create `config.env` or set environment variables.
6.  Run the bot: `python3 main.py`
7.  Run the web server (needed for some platforms/keep-alive): `gunicorn app:app --bind 0.0.0.0:8000` (Adjust port as needed)

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.
