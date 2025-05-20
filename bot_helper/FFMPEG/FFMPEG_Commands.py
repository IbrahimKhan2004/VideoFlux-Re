# --- START OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Commands.py ---

from bot_helper.Database.User_Data import get_data
from bot_helper.Others.Helper_Functions import get_video_duration
from bot_helper.Others.Names import Names
# Highlighted change: Import os.path for splitext
from os.path import isdir, splitext, exists, splitext as os_path_splitext
# End of highlighted change
from os import makedirs, remove
# Highlighted change: Import math for ceil used in bufsize calculation
from math import ceil
# START OF MODIFIED BLOCK
from config.config import LOGGER # Import LOGGER
# END OF MODIFIED BLOCK

def create_direc(direc):
    if not isdir(direc):
        makedirs(direc)
    return


def get_output_name(process_status, convert_quality=False):
    if process_status.file_name:
            out_file_name = process_status.file_name
    else:
            out_file_name = process_status.send_files[-1].split("/")[-1]
    # Modified to use video quality string if present
    if convert_quality and isinstance(convert_quality, str) and '[' in convert_quality:
        base_name, extension = os_path_splitext(out_file_name) # Use imported splitext
        # Extract resolution like 720p from "720p [1280x720]"
        quality_tag = convert_quality.split(' ')[0]
        out_file_name = f"{base_name}_{quality_tag}{extension}"
    elif convert_quality and isinstance(convert_quality, int): # Fallback for old integer quality
        base_name, extension = os_path_splitext(out_file_name) # Use imported splitext
        out_file_name = f"{base_name}_{str(convert_quality)}p{extension}"
    # Added else case to handle when convert_quality is not provided or not in expected format
    else:
        # Keep original name if quality info is not applicable/available
        pass
    return out_file_name


def get_commands(process_status):
    # REMOVED: Compress command block
    # if process_status.process_type==Names.compress:
    #         ... (block content removed) ...

    # REMOVED: Watermark command block
    # elif process_status.process_type==Names.watermark:
    #     ... (block content removed) ...

    if process_status.process_type==Names.merge: # MODIFIED: Changed elif to if
            merge_map = get_data()[process_status.user_id]['merge']['map'] # Yeh setting abhi bhi use ho sakti hai decide karne ke liye ki map karna hai ya nahi
            merge_fix_blank = get_data()[process_status.user_id]['merge']['fix_blank']
            create_direc(f"{process_status.dir}/merge/")
            log_file = f"{process_status.dir}/merge/merge_logs_{process_status.process_id}.txt"
            infile_names = ""
            file_duration =0
            for dwfile_loc in process_status.send_files:
                escaped_dwfile_loc = str(dwfile_loc).replace("'", "'\\''") # Escape single quotes for concat demuxer
                infile_names += f"file '{escaped_dwfile_loc}'\n"
                file_duration += get_video_duration(dwfile_loc)
            input_file = f"{process_status.dir}/merge/merge_files.txt"
            with open(input_file, "w", encoding="utf-8") as f:
                        f.write(str(infile_names).strip('\n'))
            # Highlighted change: Force .mkv extension for merge output
            base_output_name, _ = os_path_splitext(get_output_name(process_status)) # Get name without extension
            output_file = f"{process_status.dir}/merge/{base_output_name}.mkv" # Force .mkv extension
            # End of highlighted change
            command = ['ffmpeg','-hide_banner', # Reverted zender -> ffmpeg
                                    '-progress', f"{log_file}",
                                        "-f", "concat",
                                        "-safe", "0",
                                        "-ignore_unknown"] # Added -ignore_unknown flag
            if merge_fix_blank:
                command += ['-segment_time_metadata', '1']
            command+=["-i", f'{str(input_file)}']
            if merge_fix_blank:
                command += ['-vf', 'select=concatdec_select', '-af', 'aselect=concatdec_select,aresample=async=1']
# START OF MODIFIED BLOCK ###################################################
            if merge_map: # Agar user ne settings mein map True rakha hai
                command+=['-map','0:v?', # Video streams map karo (agar hain)
                           '-map','0:a?', # Audio streams map karo (agar hain)
                           '-map','0:s?'] # Subtitle streams map karo (agar hain)
                # Attachments (0:t) ko yahan explicitly map nahi kiya gaya hai
            # Agar merge_map False hai, toh FFmpeg default stream selection karega (usually best video, best audio)
            # ya fir agar -c copy hai toh specific mapping zaroori ho jaati hai.
            # Is case mein, agar merge_map False hai aur -c copy hai, toh FFmpeg error de sakta hai.
            # Behtar hai ki merge_map hamesha True rakha jaaye merge ke liye aur specific streams map kiye jaayein.
            # For simplicity, assuming merge_map True means we want video, audio, subtitles.
# END OF MODIFIED BLOCK #####################################################
            if not merge_fix_blank:
                command+= ["-c", "copy"]
# START OF MODIFIED BLOCK
            # Apply Global and Fixed Metadata for Merge
            custom_metadata_text = get_data()[process_status.user_id].get('metadata', '')
            is_custom_metadata_enabled = get_data()[process_status.user_id].get('custom_metadata', False)

            if is_custom_metadata_enabled and custom_metadata_text:
                LOGGER.info(f"Applying User's Global Metadata Text to Merge: '{custom_metadata_text}'")
                command += ['-metadata', f'title={custom_metadata_text}']
                command += ['-metadata', f'author={custom_metadata_text}']
                command += ['-metadata', f'encoded_by={custom_metadata_text}']
                command += ['-metadata', f'comment={custom_metadata_text}']
                command += ['-metadata:s:v:0', f'title={custom_metadata_text}']
                command += ['-metadata:s:a', f'title={custom_metadata_text}']
                command += ['-metadata:s:s', f'title={custom_metadata_text}'] # Assumes subtitles are part of the input files being merged

            command += ['-metadata', 'description=Visit TG-@Eliteflix_Official']
            command += ['-metadata', 'telegram=Downloaded From @Eliteflix_Official']
            LOGGER.info("Applied fixed metadata (Description, Telegram) to Merge.")
# END OF MODIFIED BLOCK
            command+= ['-y', f'{str(output_file)}'] # Use the modified output_file
            return command, log_file, input_file, output_file, file_duration

    elif process_status.process_type==Names.softmux:
        softmux_preset =  get_data()[process_status.user_id]['softmux']['preset']
        softmux_crf = get_data()[process_status.user_id]['softmux']['crf']
        softmux_use_crf = get_data()[process_status.user_id]['softmux']['use_crf']
        softmux_encode = get_data()[process_status.user_id]['softmux']['encode']
        create_direc(f"{process_status.dir}/softmux/")
        log_file = f"{process_status.dir}/softmux/softmux_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/softmux/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        input_sub = []
        sub_map = []
        smap = 1
        for subtitle in process_status.subtitles:
            input_sub += ['-i', f'{str(subtitle)}']
            sub_map+= ['-map', f'{smap}:0'] # Map subtitle stream from its own input
            smap +=1
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}'] # Reverted zender -> ffmpeg
        command+= input_sub # Add subtitle inputs
        # Map video, audio from main input, then map subtitle streams from their respective inputs
        command+= ['-map','0:v?', '-map',f'0:a?'] # Use 0:a? to map all audio from main input
        for i in range(len(process_status.subtitles)):
            command+= ['-map', f'{i+1}:s:0'] # Map the first subtitle stream from each subtitle input file
        command+= ['-disposition:s:0','default'] # Set first overall subtitle track as default (optional)

        if softmux_encode: # If video re-encoding is enabled for softmux
                encoder = get_data()[process_status.user_id]['softmux']['encoder']
                if softmux_use_crf:
                        if encoder=='libx265':
                                command += ['-c:v','libx265', '-vtag', 'hvc1', '-crf', f'{str(softmux_crf)}', '-preset', softmux_preset]
                        else:
                                command += ['-c:v','libx264', '-crf', f'{str(softmux_crf)}', '-preset', softmux_preset]
                else:
                        if encoder=='libx265':
                                command += ['-c:v','libx265', '-vtag', 'hvc1', '-preset', softmux_preset]
                        else:
                                command += ['-c:v','libx264', '-preset', softmux_preset]
                command += ['-c:a', 'copy'] # Typically audio is copied in softmux unless specified otherwise
        else: # If not re-encoding video, copy video and audio
                command += ['-c:v','copy', '-c:a', 'copy']

        command += ["-c:s", f"{get_data()[process_status.user_id]['softmux']['sub_codec']}"] # Set subtitle codec (e.g., copy, mov_text)

# START OF MODIFIED BLOCK
        # Apply Global and Fixed Metadata for Softmux
        custom_metadata_text = get_data()[process_status.user_id].get('metadata', '')
        is_custom_metadata_enabled = get_data()[process_status.user_id].get('custom_metadata', False)

        if is_custom_metadata_enabled and custom_metadata_text:
            LOGGER.info(f"Applying User's Global Metadata Text to Softmux: '{custom_metadata_text}'")
            command += ['-metadata', f'title={custom_metadata_text}']
            command += ['-metadata', f'author={custom_metadata_text}']
            command += ['-metadata', f'encoded_by={custom_metadata_text}']
            command += ['-metadata', f'comment={custom_metadata_text}']
            command += ['-metadata:s:v:0', f'title={custom_metadata_text}']
            command += ['-metadata:s:a', f'title={custom_metadata_text}']
            # For softmux, subtitles are separate streams, apply title to them if desired
            # This will apply to all output subtitle streams
            command += ['-metadata:s:s', f'title={custom_metadata_text}']


        command += ['-metadata', 'description=Visit TG-@Eliteflix_Official']
        command += ['-metadata', 'telegram=Downloaded From @Eliteflix_Official']
        LOGGER.info("Applied fixed metadata (Description, Telegram) to Softmux.")
# END OF MODIFIED BLOCK
        command += ["-y", f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration

    # REMOVED: SoftReMux command block
    # elif process_status.process_type==Names.softremux:
    #     ... (block content removed) ...


    elif process_status.process_type==Names.convert:
            # --- Start of VFBITMOD-update Integration ---
            convert_preset =  get_data()[process_status.user_id]['convert']['preset']
            convert_vbit = get_data()[process_status.user_id]['video']['vbit']
            convert_abit = get_data()[process_status.user_id]['abit'] if get_data()[process_status.user_id]['use_abit'] else None # Use custom if enabled
            convert_acodec = get_data()[process_status.user_id]['audio']['acodec']
            convert_achannel = get_data()[process_status.user_id]['audio']['achannel']
            convert_map = get_data()[process_status.user_id]['convert']['map']
            convert_encoder = get_data()[process_status.user_id]['video']['encude']
            convert_copysub = get_data()[process_status.user_id]['convert']['copy_sub']
            convert_sync = get_data()[process_status.user_id]['convert']['sync']
            convert_encode_mode = get_data()[process_status.user_id]['convert']['encode'] # Renamed to avoid conflict
            convert_quality = get_data()[process_status.user_id]['video']['qubality'] # e.g., '720p [1280x720]'
            convert_type = get_data()[process_status.user_id]['convert']['type'] # CRF or VBR or ABR or CBR
            convert_crf = get_data()[process_status.user_id]['crf'] if get_data()[process_status.user_id]['use_crf'] else None # Use custom if enabled
            convert_vbr = get_data()[process_status.user_id]['vbr'] if get_data()[process_status.user_id]['use_vbr'] else None # Use custom if enabled
            convert_abr = get_data()[process_status.user_id]['abr'] if get_data()[process_status.user_id]['use_abr'] else None # Use custom if enabled
            # Highlighted change: Get CBR setting
            convert_cbr = get_data()[process_status.user_id]['cbr'] if get_data()[process_status.user_id]['use_cbr'] else None # Use custom if enabled
# Highlighted change: Get tune setting
            video_tune = get_data()[process_status.user_id]['video']['tune']
# START OF MODIFIED BLOCK
# Highlighted change: Get target size settings
            use_target_size = get_data()[process_status.user_id].get('use_target_size', False)
            target_size_mb = get_data()[process_status.user_id].get('target_size_mb', 0) # Get as int
            use_calculated_abr_for_video = False # Flag to indicate if target size calculation was used
            calculated_video_bitrate_str = None # Store calculated video bitrate
# END OF MODIFIED BLOCK
# End of highlighted change
            # --- End of VFBITMOD-update Integration ---

            create_direc(f"{process_status.dir}/convert/")
            log_file = f"{process_status.dir}/convert/convert_logs_{process_status.process_id}.txt"
            if exists(log_file):
                remove(log_file)
            input_file = f'{str(process_status.send_files[-1])}'
            # Use the new quality string for output name generation
            output_file = f"{process_status.dir}/convert/{get_output_name(process_status, convert_quality=convert_quality)}"
            file_duration = get_video_duration(input_file)

            # Highlighted change: Added -nostdin flag
            command = ['ffmpeg', '-nostdin', '-hide_banner', # Reverted zender -> ffmpeg, Added -nostdin
            # End of highlighted change
                                            '-progress', f"{log_file}",
                                            '-i', f'{input_file}']

# START OF MODIFIED BLOCK
            _final_audio_codec_for_calc = convert_acodec # To store potentially overridden audio codec for target size
            _final_audio_bitrate_str_for_calc = convert_abit # To store potentially overridden audio bitrate for target size
            # --- Start of Target File Size Logic ---
            if use_target_size and target_size_mb > 0 and file_duration > 0:
                process_status.update_process_message(f"🎯Calculating for Target Size: {target_size_mb}MB\n{process_status.get_task_details()}")
                LOGGER.info(f"Target Size Mode: Aiming for ~{target_size_mb} MB for {input_file}.") # Use LOGGER

                # Use local copies for calculation to avoid modifying original settings if calculation fails
                _calc_audio_codec = convert_acodec
                _calc_audio_bitrate = convert_abit
                _default_forced_audio_codec = "aac"
                _default_forced_audio_bitrate = "128k"

                if _calc_audio_codec.lower() == "copy":
                    LOGGER.warning(f"Target Size Mode: Audio codec was 'copy', overriding to '{_default_forced_audio_codec}' for calculation.") # Use LOGGER
                    _calc_audio_codec = _default_forced_audio_codec
                    if not _calc_audio_bitrate: # If audio was copy AND no custom abit was set
                        _calc_audio_bitrate = _default_forced_audio_bitrate
                        LOGGER.info(f"Target Size Mode: Audio bitrate for 'copy' not set, using default '{_calc_audio_bitrate}'.") # Use LOGGER
                elif not _calc_audio_bitrate: # Audio re-encode selected, but no bitrate
                    LOGGER.warning(f"Target Size Mode: Audio codec is '{_calc_audio_codec}', but no audio bitrate. Using default '{_default_forced_audio_bitrate}'.") # Use LOGGER
                    _calc_audio_bitrate = _default_forced_audio_bitrate
                
                _final_audio_codec_for_calc = _calc_audio_codec
                _final_audio_bitrate_str_for_calc = _calc_audio_bitrate


                target_total_bits = target_size_mb * 1024 * 1024 * 8
                audio_bitrate_bps_for_calc = 0
                try:
                    if not _final_audio_bitrate_str_for_calc:
                        raise ValueError("Audio bitrate for calculation is unexpectedly empty.")
                    if 'k' in _final_audio_bitrate_str_for_calc.lower():
                        audio_bitrate_bps_for_calc = int(_final_audio_bitrate_str_for_calc.lower().replace('k', '')) * 1000
                    elif 'm' in _final_audio_bitrate_str_for_calc.lower():
                        audio_bitrate_bps_for_calc = int(float(_final_audio_bitrate_str_for_calc.lower().replace('m', '')) * 1000000)
                    else:
                        audio_bitrate_bps_for_calc = int(_final_audio_bitrate_str_for_calc)
                except ValueError as e_parse_audio_br:
                    LOGGER.error(f"Target Size Mode: Error parsing determined audio bitrate '{_final_audio_bitrate_str_for_calc}': {e_parse_audio_br}. Using fallback 128kbps for calculation.") # Use LOGGER
                    audio_bitrate_bps_for_calc = 128 * 1000
                    _final_audio_bitrate_str_for_calc = "128k" # Ensure this is updated for FFmpeg command
                    if _final_audio_codec_for_calc.lower() == "copy": # Should have been caught above, but defensive
                         _final_audio_codec_for_calc = _default_forced_audio_codec


                audio_total_bits_for_file = audio_bitrate_bps_for_calc * file_duration
                overhead_factor = 0.03 
                estimated_overhead_bits = target_total_bits * overhead_factor
                remaining_bits_for_video = target_total_bits - audio_total_bits_for_file - estimated_overhead_bits

                if remaining_bits_for_video > 0:
                    calculated_video_bitrate_bps = int(remaining_bits_for_video / file_duration)
                    min_video_bitrate_bps = 100 * 1000
                    calculated_video_bitrate_bps = max(calculated_video_bitrate_bps, min_video_bitrate_bps)
                    calculated_video_bitrate_str = f"{calculated_video_bitrate_bps // 1000}k"

                    LOGGER.info(f"Target Size Mode: Calculated target video bitrate: {calculated_video_bitrate_str}") # Use LOGGER
                    LOGGER.info(f"Target Size Mode: Audio will be: '{_final_audio_codec_for_calc}' at '{_final_audio_bitrate_str_for_calc}' (used for calculation).") # Use LOGGER
                    use_calculated_abr_for_video = True
                else:
                    LOGGER.warning(f"Target Size Mode: Target file size {target_size_mb}MB is too small for the video duration ({file_duration}s) and determined audio bitrate '{_final_audio_bitrate_str_for_calc}'. Video will use standard rate control settings from user.") # Use LOGGER
                    use_calculated_abr_for_video = False

            elif use_target_size and target_size_mb > 0 and file_duration <= 0:
                LOGGER.warning("Target Size Mode: Cannot determine video duration. Target file size feature disabled for this conversion.") # Use LOGGER
            elif use_target_size and target_size_mb <= 0: # User explicitly set target to 0 or less
                LOGGER.info("Target Size Mode: Disabled by user (Target MB is 0 or less).") # Use LOGGER
            # --- End of Target File Size Logic ---
# END OF MODIFIED BLOCK

            # --- Start of VFBITMOD-update Command Logic ---
            # Video Encoding Part
            if convert_encode_mode == 'Video' or convert_encode_mode == 'Video Audio [Both]': # Use renamed variable
                # Resolution Scaling
                if convert_quality=='480p [720x360]':
                    command+=['-vf', 'scale=720:360']
                elif convert_quality=='480p [720x480]':
                    command+=['-vf', 'scale=720:480']
# Highlighted change: Added scaling for 576p and 648p
                elif convert_quality=='576p [1024x576]':
                    command+=['-vf', 'scale=1024:576']
                elif convert_quality=='648p [1152x648]':
                    command+=['-vf', 'scale=1152:648']
# End of highlighted change
                elif convert_quality=='720p [1280x640]':
                    command+=['-vf', 'scale=1280:640']
                elif convert_quality=='720p [1280x720]':
                    command+=['-vf', 'scale=1280:720']
                elif convert_quality=='1080p [1920x960]':
                    command+=['-vf', 'scale=1920:960']
                else: # Default to 1080p [1920x1080]
                     command+=['-vf', 'scale=1920:1080']

                # Pixel Format (Bit Depth)
                if convert_vbit=='8Bit':
                    command+= ['-pix_fmt','yuv420p']
                else: # 10Bit
                    command+= ['-pix_fmt','yuv420p10le']

                # Video Codec
                if convert_encoder=='HEVC':
                    command+= ['-vcodec','libx265','-vtag', 'hvc1']
# Highlighted change: Add VP9 encoder logic with threading
                elif convert_encoder=='VP9':
                    command+= ['-vcodec','libvpx-vp9']
                    # Map preset to cpu-used and set deadline
                    command+= ['-deadline', 'good'] # Common deadline
                    # Add automatic threads and row-mt
                    command+= ['-threads', '0'] # Auto-detect threads
                    command+= ['-row-mt', '1']  # Enable row multi-threading
                    # Set cpu-used based on preset
                    if convert_preset == 'ultrafast':
                        command+= ['-cpu-used', '5']
                    elif convert_preset == 'superfast':
                        command+= ['-cpu-used', '4']
                    elif convert_preset == 'veryfast':
                        command+= ['-cpu-used', '3']
                    elif convert_preset == 'faster':
                        command+= ['-cpu-used', '2']
                    elif convert_preset == 'fast':
                        command+= ['-cpu-used', '1']
                    else: # medium, slow, slower, veryslow map to best quality
                        command+= ['-cpu-used', '0']
# End of highlighted change
                else: # H.264
                    command+= ['-vcodec','libx264']

# Highlighted change: Add tune setting if not 'None' and encoder is not VP9
                # Tune Setting
                if video_tune != 'None' and convert_encoder != 'VP9':
                    command += ['-tune', video_tune]
# End of highlighted change

# START OF MODIFIED BLOCK
                # Rate Control (CRF, VBR, ABR, or CBR) - Target Size ABR takes precedence
                if use_calculated_abr_for_video and calculated_video_bitrate_str:
                    LOGGER.info(f"Applying calculated ABR video bitrate for Target Size: {calculated_video_bitrate_str}") # Use LOGGER
                    command += ['-b:v', calculated_video_bitrate_str]
                    # If VP9, ensure -b:v 0 is NOT set when using target ABR
                    if convert_encoder == 'VP9':
                        # VP9 ABR doesn't need -b:v 0. cpu-used and deadline are already set.
                        pass
# END OF MODIFIED BLOCK
                elif convert_type=='CRF' and convert_crf is not None:
                    command+= ['-crf', f'{str(convert_crf)}']
# Highlighted change: Add -b:v 0 for VP9 CRF
                    if convert_encoder == 'VP9':
                        command+= ['-b:v', '0'] # Required for VP9 CRF
# End of highlighted change
                elif convert_type=='VBR' and convert_vbr is not None:
                    command+= ['-b:v', f'{str(convert_vbr)}']
                elif convert_type=='ABR' and convert_abr is not None:
                    command+= ['-b:v', f'{str(convert_abr)}'] # ABR (1-pass) uses -b:v
# Highlighted change: Added CBR handling (only if not VP9)
                elif convert_type=='CBR' and convert_cbr is not None and convert_encoder != 'VP9':
                    # For CBR, set minrate, maxrate same as bitrate, and bufsize (e.g., 2*bitrate)
                    bitrate_str = str(convert_cbr)
                    bufsize_str = bitrate_str # Default bufsize = bitrate if parsing fails
                    try:
                        if bitrate_str.lower().endswith('k'):
                            bitrate_val = int(bitrate_str[:-1]) * 1000
                        elif bitrate_str.lower().endswith('m'):
                            bitrate_val = int(float(bitrate_str[:-1]) * 1000000)
                        else:
                            bitrate_val = int(bitrate_str) # Assume bps if no suffix

                        bufsize_val = bitrate_val * 2 # Calculate bufsize
                        # Format bufsize back to string with 'k' suffix
                        bufsize_str = f"{ceil(bufsize_val / 1000)}k"
                    except ValueError:
                        # Use default if parsing fails
                        bitrate_str = "1500k"
                        bufsize_str = "3000k"
                        pass # Keep default bufsize if parsing fails

                    command += ['-b:v', bitrate_str, '-minrate', bitrate_str, '-maxrate', bitrate_str, '-bufsize', bufsize_str]
# End of highlighted change
                # If type is set but value is None (not enabled), FFmpeg might use defaults or error.
                # Consider adding a default CRF/VBR if type is selected but value isn't enabled.
                elif convert_type=='CRF': # Default CRF if enabled but no value set
                     command+= ['-crf', '23'] # Example default
# Highlighted change: Add -b:v 0 for VP9 CRF default
                     if convert_encoder == 'VP9':
                         command+= ['-b:v', '0'] # Required for VP9 CRF
# End of highlighted change
                elif convert_type=='VBR': # Default VBR if enabled but no value set
                     command+= ['-b:v', '1500k'] # Example default
                elif convert_type=='ABR': # Default ABR if enabled but no value set
                     command+= ['-b:v', '1500k'] # Example default
# Highlighted change: Added CBR default fallback (only if not VP9)
                elif convert_type=='CBR' and convert_encoder != 'VP9': # Default CBR if enabled but no value set
                     command += ['-b:v', '1500k', '-minrate', '1500k', '-maxrate', '1500k', '-bufsize', '3000k'] # Example default
# End of highlighted change

            else: # Only Audio encode or no video encode (i.e. convert_encode_mode == 'Audio')
                command+=['-c:v', 'copy']

# START OF MODIFIED BLOCK
            # Audio Encoding Part - Respect Target Size Mode decisions for audio
            if convert_encode_mode == 'Audio' or convert_encode_mode == 'Video Audio [Both]':
                _actual_audio_codec_to_use = convert_acodec
                _actual_audio_bitrate_to_use = convert_abit

                if use_target_size and target_size_mb > 0 and file_duration > 0 and use_calculated_abr_for_video: # Ensure target size was active AND successfully calculated
                    # Use the potentially overridden audio settings from target size calculation
                    _actual_audio_codec_to_use = _final_audio_codec_for_calc
                    _actual_audio_bitrate_to_use = _final_audio_bitrate_str_for_calc
                    LOGGER.info(f"Target Size Mode: Applying audio codec '{_actual_audio_codec_to_use}' and bitrate '{_actual_audio_bitrate_to_use}' for FFmpeg.")


                if _actual_audio_codec_to_use.lower() == 'copy' and not (use_target_size and target_size_mb > 0 and file_duration > 0 and use_calculated_abr_for_video) : # only copy if not overridden by target size
                    command += ['-c:a', 'copy']
                else:
                    # Audio Codec
                    if _actual_audio_codec_to_use.lower()=='opus':
                        codec = 'libopus'
                    elif _actual_audio_codec_to_use.lower()=='dd': # Dolby Digital (AC3)
                        codec = 'ac3'
                    elif _actual_audio_codec_to_use.lower()=='ddp': # Dolby Digital Plus (E-AC3)
                        codec = 'eac3'
                    else: # Default AAC or user-specified if not copy
                        codec = 'aac'
                    command += ['-c:a', codec]

                    # Audio Bitrate (only if custom is enabled or set by target size)
                    if _actual_audio_bitrate_to_use:
                        command += ['-b:a', f'{str(_actual_audio_bitrate_to_use)}']

                # Audio Channels (always apply user's choice unless it was 'copy' and overridden by target size logic needing re-encode)
                if convert_achannel.lower() != "copy":
                    command += ['-ac', f'{str(convert_achannel)}']
                # If convert_achannel is 'copy' AND target size mode forced re-encode, FFmpeg will pick channels or use source.
                # If convert_achannel is 'copy' AND audio is copied (no target size override), then channels are copied.
            else: # No audio encode (video only, or if convert_encode_mode was 'Video' and target size was not active)
                command+= ['-c:a', 'copy']
# END OF MODIFIED BLOCK

            # Common Settings
            if convert_map:
                command+=['-map','0:v?',
                                            '-map',f'{str(process_status.amap_options)}?', # This maps the audio selected by user/default
                                            "-map", "0:s?"] # Map all subtitle streams from input 0
            if convert_copysub:
                command+= ["-c:s", "copy"] # Copy subtitle streams if enabled

            convert_use_queue_size = get_data()[process_status.user_id]['convert']['use_queue_size']
            if convert_use_queue_size:
                convert_queue_size = get_data()[process_status.user_id]['convert']['queue_size']
                command+= ['-max_muxing_queue_size', f'{str(convert_queue_size)}']
            if convert_sync:
                command+= ['-vsync', '1', '-async', '-1']

# Highlighted change: Apply preset only if not VP9
            if convert_encoder != 'VP9':
                command+= ['-preset', convert_preset]
# End of highlighted change

# START OF MODIFIED BLOCK
            # Metadata part for Convert
            custom_metadata_text = get_data()[process_status.user_id].get('metadata', '')
            is_custom_metadata_enabled = get_data()[process_status.user_id].get('custom_metadata', False)

            if is_custom_metadata_enabled and custom_metadata_text:
                LOGGER.info(f"Applying User's Global Metadata Text to Convert: '{custom_metadata_text}'")
                command += ['-metadata', f'title={custom_metadata_text}']
                command += ['-metadata', f'author={custom_metadata_text}']
                command += ['-metadata', f'encoded_by={custom_metadata_text}']
                command += ['-metadata', f'comment={custom_metadata_text}']
                command += ['-metadata:s:v:0', f'title={custom_metadata_text}']
                command += ['-metadata:s:a', f'title={custom_metadata_text}']
                if convert_copysub: # Apply to subtitles only if they are being copied
                    command += ['-metadata:s:s', f'title={custom_metadata_text}']

            command += ['-metadata', 'description=Visit TG-@Eliteflix_Official']
            command += ['-metadata', 'telegram=Downloaded From @Eliteflix_Official']
            LOGGER.info("Applied fixed metadata (Description, Telegram) to Convert.")
# END OF MODIFIED BLOCK

            command+= ['-y', f"{output_file}"]
            # --- End of VFBITMOD-update Command Logic ---

            return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.hardmux:
        hardmux_preset =  get_data()[process_status.user_id]['hardmux']['preset']
        hardmux_crf = get_data()[process_status.user_id]['hardmux']['crf']
        hardmux_encode_video = get_data()[process_status.user_id]['hardmux']['encode_video']
        create_direc(f"{process_status.dir}/hardmux/")
        log_file = f"{process_status.dir}/hardmux/hardmux_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/hardmux/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        sub_loc = process_status.subtitles[-1]
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}'] # Reverted zender -> ffmpeg
        command+= ['-vf', f"subtitles='{sub_loc}'", # Subtitles are burned in, so they become part of video stream
                                    '-map','0:v', # Map video
                                    '-map',f'{str(process_status.amap_options)}?'] # Map selected/all audio
                                    # No -map 0:s? needed as subtitles are part of video filter
        if hardmux_encode_video:
                encoder = get_data()[process_status.user_id]['hardmux']['encoder']
                if encoder=='libx265':
                        command += ['-c:v','libx265', '-vtag', 'hvc1', '-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset]
                else:
                        command += ['-c:v','libx264', '-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset]
                command += ['-c:a','copy'] # Audio is copied if video is re-encoded
        else: # If not encoding video, copy video and audio
                command += ['-c:v','copy', '-c:a','copy']

        hardmux_sync = get_data()[process_status.user_id]['hardmux']['sync']
        hardmux_use_queue_size = get_data()[process_status.user_id]['hardmux']['use_queue_size']
        if hardmux_use_queue_size:
                hardmux_queue_size = get_data()[process_status.user_id]['hardmux']['queue_size']
                command+= ['-max_muxing_queue_size', f'{str(hardmux_queue_size)}']
        if hardmux_sync:
            command+= ['-vsync', '1', '-async', '-1']

# START OF MODIFIED BLOCK
        # Apply Global and Fixed Metadata for Hardmux
        custom_metadata_text = get_data()[process_status.user_id].get('metadata', '')
        is_custom_metadata_enabled = get_data()[process_status.user_id].get('custom_metadata', False)

        if is_custom_metadata_enabled and custom_metadata_text:
            LOGGER.info(f"Applying User's Global Metadata Text to Hardmux: '{custom_metadata_text}'")
            command += ['-metadata', f'title={custom_metadata_text}']
            command += ['-metadata', f'author={custom_metadata_text}']
            command += ['-metadata', f'encoded_by={custom_metadata_text}']
            command += ['-metadata', f'comment={custom_metadata_text}']
            command += ['-metadata:s:v:0', f'title={custom_metadata_text}'] # Video stream title
            command += ['-metadata:s:a', f'title={custom_metadata_text}']   # Audio stream titles
            # No -metadata:s:s for hardmux as subtitles are part of the video stream

        command += ['-metadata', 'description=Visit TG-@Eliteflix_Official']
        command += ['-metadata', 'telegram=Downloaded From @Eliteflix_Official']
        LOGGER.info("Applied fixed metadata (Description, Telegram) to Hardmux.")
# END OF MODIFIED BLOCK

        command += ["-y", f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.changeMetadata:
        create_direc(f"{process_status.dir}/metadata/")
        log_file = f"{process_status.dir}/metadata/metadata_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/metadata/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        custom_metadata = process_status.custom_metadata
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}'] # Reverted zender -> ffmpeg
        # For changeMetadata, only apply what the user specifically provides via the command arguments
        if custom_metadata: # custom_metadata is a list of lists like [['-metadata:s:a:0', 'language=eng'], ...]
            for m_list in custom_metadata:
                command += m_list
            LOGGER.info(f"Applying user-specified metadata changes for changeMetadata: {custom_metadata}")
        else: # Fallback if somehow custom_metadata is empty but command was called
            LOGGER.warning("changeMetadata called but no specific metadata changes provided by user.")
            # Optionally, apply global title if nothing else is specified, or just copy.
            # For now, let's stick to only applying user's specific changes for this command.
            # If user wants global title, they should use /convert or other processes.
            # custom_metadata_title = get_data()[process_status.user_id]['metadata']
            # command += ['-metadata', f"title={custom_metadata_title}"]
            pass


        # Added global title metadata from VFBITMOD-update - RECONSIDERED: For changeMetadata, we should only apply user's specific changes.
        # custom_metadata_title = get_data()[process_status.user_id]['metadata']
        # command += ['-metadata', f"title={custom_metadata_title}"]
        # End of Added global title metadata
        command += ["-map", "0", "-c", "copy", '-y', f"{output_file}"] # Map all streams and copy
        return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.changeindex:
        create_direc(f"{process_status.dir}/index/")
        log_file = f"{process_status.dir}/index/index_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/index/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        # For changeindex, metadata is typically just copied with the streams. No additional global/fixed tags.
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}', '-map', '0:v?'] + process_status.custom_index # Reverted zender -> ffmpeg
        command += ["-c", "copy", '-y', f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration

# --- END OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Commands.py ---
