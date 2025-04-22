# --- START OF FILE VideoFlux-Re-master/bot_helper/Others/Names.py ---

class Names:
    # REMOVED: compress name
    # compress = "Compress"
    # REMOVED: watermark name
    # watermark = "Watermark"
    merge = "Merge"
    softmux = "SoftMux"
    # REMOVED: softremux name
    # softremux = "SoftReMux"
    convert = "Convert"
    hardmux = "Hardmux"
    aria = "Aria"
    ffmpeg = "FFMPEG"
    telethon = "Telethon"
    pyrogram = "Pyrogram"
    rclone = "Rclone"
    gensample = "VideoSample"
    genss ="GenSS"
# <<<< START OF DELETED BLOCK >>>>
#     leech="Leech"
#     mirror="Mirror"
# <<<< END OF DELETED BLOCK >>>>
    changeMetadata = 'ChangeMetadata'
    changeindex = "ChangeIndex"
    STATUS = { # MODIFIED: Removed compress, watermark, softremux entries
                        # compress: "🏮Compressing",
                        # watermark: "🛺Adding Watermark",
                        merge: "🍧Merging",
                        softmux: "🎮SoftMuxing Subtitles",
                        # softremux: "🛩SoftReMuxing Subtitles",
                        convert: "🚜Converting Video",
                        hardmux: "🚍HardMuxing Subtitle",
                        changeMetadata: "🪀Changing MetaData",
                        changeindex: "🎨Changing Index"}
    FFMPEG_PROCESSES = [ # MODIFIED: Removed compress, watermark, softremux entries
                                                        # compress,
                                                        # watermark,
                                                        merge,
                                                        softmux,
                                                        # softremux,
                                                        convert,
                                                        hardmux,
                                                        changeMetadata,
                                                        changeindex]
    STATUS_UPLOADING = "🔼Uploading"
    STATUS_CLONING= "🧬Cloning"
    STATUS_DOWNLOADING = "🔽Downloading"
    STATUS_COPYING= "🔁Copying"
    STATUS_ARCHIVING = "🔐Archiving"
    STATUS_EXTRACTING = "📂Extracting"
    STATUS_SPLITTING = "✂️Splitting"
    STATUS_SYNCING= "Syncing"
    STATUS_WAITING = "Queue"
    STATUS_PAUSED = "Pause"
    STATUS_CHECKING = "CheckUp"
    STATUS_SEEDING = "Seed"

# --- END OF FILE VideoFlux-Re-master/bot_helper/Others/Names.py ---
