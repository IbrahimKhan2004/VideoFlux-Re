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
# START OF MODIFIED BLOCK
            user_settings = get_data()[process_status.user_id]
            apply_user_metadata_globally = user_settings.get('custom_metadata', False)
            user_global_metadata_text = user_settings.get('metadata', "VideoFlux Default Title") # Existing text field
# END OF MODIFIED BLOCK
            merge_map = get_data()[process_status.user_id]['merge']['map'] # Yeh setting abhi bhi use ho sakti hai decide karne ke liye ki map karna hai ya nahi
            merge_fix_blank = get_data()[process_status.user_id]['merge']['fix_blank']
# HIGHLIGHTED CHANGE START: Get merge_fix_timestamps setting
            merge_fix_timestamps = get_data()[process_status.user_id]['merge'].get('fix_timestamps', False)
# HIGHLIGHTED CHANGE END
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
# <<<< MODIFIED LINES START >>>>
                                    '-analyzeduration', '500M', # Increased analyzeduration for concat
                                    '-probesize', '500M',       # Increased probesize for concat
# <<<< MODIFIED LINES END >>>>
                                    '-progress', f"{log_file}"]
# HIGHLIGHTED CHANGE START: Modify -fflags based on merge_fix_timestamps
            fflags_options = "+genpts"
            if merge_fix_timestamps:
                fflags_options += "+igndts"
            command += ['-fflags', fflags_options]
# HIGHLIGHTED CHANGE END
            command += [        "-f", "concat",
                                        "-safe", "0",
                                        "-autorotate", "0",
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
            # ya fir agar agar -c copy hai toh specific mapping zaroori ho jaati hai.
            # Is case mein, agar merge_map False hai aur -c copy hai, toh FFmpeg error de sakta hai.
            # Behtar hai ki merge_map hamesha True rakha jaaye merge ke liye aur specific streams map kiye jaayein.
            # For simplicity, assuming merge_map True means we want video, audio, subtitles.
# END OF MODIFIED BLOCK #####################################################
# HIGHLIGHTED CHANGE START: Fix for subtitle copying in merge
            if merge_fix_blank:
                if not merge_map: # If merge_map was false, subtitles weren't mapped yet by the block above
                    command += ['-map', '0:s?'] # Map subtitle streams
                command += ['-c:s', 'srt'] # Ensure subtitle streams are converted to srt
# HIGHLIGHTED CHANGE END: Fix for subtitle copying in merge
            if not merge_fix_blank:
                command+= ['-c:v', 'copy', '-c:a', 'copy', '-c:s', 'srt'] # Copy video/audio, convert subtitles to srt
# START OF MODIFIED BLOCK
            # Apply metadata if user has it enabled
            if apply_user_metadata_globally:
                LOGGER.info(f"MERGE: Applying custom metadata. User text: '{user_global_metadata_text}'")
                # User's text for main title and stream titles (VideoFlux already did this part)
                command.extend(['-metadata', f'title={user_global_metadata_text}'])
                command.extend(['-metadata:s:v', f'title={user_global_metadata_text}'])
                command.extend(['-metadata:s:a', f'title={user_global_metadata_text}'])
                command.extend(['-metadata:s:s', f'title={user_global_metadata_text}'])

                # User's text for author and comment
                command.extend(['-metadata', f'author={user_global_metadata_text}'])
                command.extend(['-metadata', f'comment={user_global_metadata_text}'])

                # Fixed fields
                command.extend(['-metadata', 'encoded_by=[ BashAFK ~ TG_Eliteflix_Official ]'])
                command.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
                command.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
                LOGGER.info("MERGE: Applied fixed metadata: encoded_by, description, telegram tags.")
            else:
                # Fallback to original VideoFlux merge metadata if global custom_metadata is off
                # This part was already in VideoFlux for merge, using 'metadata' as custom_metadata_title
                custom_metadata_title_vf = get_data()[process_status.user_id]['metadata'] # This is the same as user_global_metadata_text
                command += ['-metadata', f"title={custom_metadata_title_vf}", '-metadata:s:v', f"title={custom_metadata_title_vf}", '-metadata:s:a', f"title={custom_metadata_title_vf}", '-metadata:s:s', f"title={custom_metadata_title_vf}"]
# END OF MODIFIED BLOCK
# HIGHLIGHTED CHANGE START: Add -avoid_negative_ts 1 and -start_at_zero based on merge_fix_timestamps
            command += ['-avoid_negative_ts', '1']
            if merge_fix_timestamps:
                command += ['-start_at_zero']
# HIGHLIGHTED CHANGE END
            command+= ['-y', f'{str(output_file)}'] # Use the modified output_file
            return command, log_file, input_file, output_file, file_duration

    elif process_status.process_type==Names.softmux:
# START OF MODIFIED BLOCK
        user_settings = get_data()[process_status.user_id]
        apply_user_metadata_globally = user_settings.get('custom_metadata', False)
        user_global_metadata_text = user_settings.get('metadata', "VideoFlux Default Title")
# END OF MODIFIED BLOCK
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
            sub_map+= ['-map', f'{smap}:0']
            smap +=1
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}'] # Reverted zender -> ffmpeg
        command+= input_sub + sub_map + ['-map','0:v?', '-map',f'{str(process_status.amap_options)}?', '-map','0:s?', '-disposition:s:0','default']
        if softmux_encode:
                encoder = get_data()[process_status.user_id]['softmux']['encoder']
                if softmux_use_crf:
                        if encoder=='libx265':
                                command += ['-vcodec','libx265', '-vtag', 'hvc1', '-crf', f'{str(softmux_crf)}', '-preset', softmux_preset]
                        else:
                                command += ['-vcodec','libx264', '-crf', f'{str(softmux_crf)}', '-preset', softmux_preset]
                else:
                        if encoder=='libx265':
                                command += ['-vcodec','libx265', '-vtag', 'hvc1', '-preset', softmux_preset]
                        else:
                                command += ['-vcodec','libx264', '-preset', softmux_preset]
        else:
                command += ['-c','copy']

        command += ["-c:s", f"{get_data()[process_status.user_id]['softmux']['sub_codec']}"]
# START OF MODIFIED BLOCK
        if apply_user_metadata_globally:
            LOGGER.info(f"SOFTMUX: Applying custom metadata. User text: '{user_global_metadata_text}'")
            if user_global_metadata_text:
                command.extend(['-metadata', f'title={user_global_metadata_text}'])
                command.extend(['-metadata', f'author={user_global_metadata_text}'])
                command.extend(['-metadata', f'comment={user_global_metadata_text}'])
                command.extend(['-metadata:s:v:0', f'title={user_global_metadata_text}'])
                command.extend(['-metadata:s:a', f'title={user_global_metadata_text}'])
                # For softmux, subtitles are separate streams, so apply title to them
                command.extend(['-metadata:s:s', f'title={user_global_metadata_text}'])
            command.extend(['-metadata', 'encoded_by=[ BashAFK ~ TG_Eliteflix_Official ]'])
            command.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
            command.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
            LOGGER.info("SOFTMUX: Applied fixed metadata tags.")
# END OF MODIFIED BLOCK
        command += ["-y", f"{output_file}"]

        return command, log_file, input_file, output_file, file_duration

    # REMOVED: SoftReMux command block
    # elif process_status.process_type==Names.softremux:
    #     ... (block content removed) ...


    elif process_status.process_type==Names.convert:
# START OF MODIFIED BLOCK
            user_settings_convert = get_data()[process_status.user_id]
            apply_user_metadata_convert = user_settings_convert.get('custom_metadata', False)
            user_global_metadata_text_convert = user_settings_convert.get('metadata', "VideoFlux Default Title")
# END OF MODIFIED BLOCK
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
            convert_encode = get_data()[process_status.user_id]['convert']['encode'] # Video, Audio, Both
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
            # --- Start of Target File Size Logic ---
            if use_target_size and target_size_mb > 0 and file_duration > 0:
                process_status.update_process_message(f"🎯Calculating for Target Size: {target_size_mb}MB\n{process_status.get_task_details()}")
                LOGGER.info(f"Target Size Mode: Aiming for ~{target_size_mb} MB for {input_file}.") # Use LOGGER

                _final_audio_codec_for_calc = convert_acodec
                _final_audio_bitrate_str_for_calc = convert_abit
                _default_forced_audio_codec = "aac" # Default if audio is 'copy' or bitrate not set
                _default_forced_audio_bitrate = "128k" # Default audio bitrate if not set

                if _final_audio_codec_for_calc.lower() == "copy":
                    LOGGER.warning(f"Target Size Mode: Audio codec was 'copy', overriding to '{_default_forced_audio_codec}' for calculation.") # Use LOGGER
                    _final_audio_codec_for_calc = _default_forced_audio_codec
                    if not _final_audio_bitrate_str_for_calc:
                        _final_audio_bitrate_str_for_calc = _default_forced_audio_bitrate
                        LOGGER.info(f"Target Size Mode: Audio bitrate for 'copy' not set, using default '{_final_audio_bitrate_str_for_calc}'.") # Use LOGGER
                elif not _final_audio_bitrate_str_for_calc: # Audio re-encode selected, but no bitrate
                    LOGGER.warning(f"Target Size Mode: Audio codec is '{_final_audio_codec_for_calc}', but no audio bitrate. Using default '{_default_forced_audio_bitrate}'.") # Use LOGGER
                    _final_audio_bitrate_str_for_calc = _default_forced_audio_bitrate

                target_total_bits = target_size_mb * 1024 * 1024 * 8
                audio_bitrate_bps_for_calc = 0
                try:
                    if not _final_audio_bitrate_str_for_calc: # Should not happen due to logic above, but as a safeguard
                        raise ValueError("Audio bitrate for calculation is unexpectedly empty.")
                    if 'k' in _final_audio_bitrate_str_for_calc.lower():
                        audio_bitrate_bps_for_calc = int(_final_audio_bitrate_str_for_calc.lower().replace('k', '')) * 1000
                    elif 'm' in _final_audio_bitrate_str_for_calc.lower(): # Support 'm' for megabits
                        audio_bitrate_bps_for_calc = int(float(_final_audio_bitrate_str_for_calc.lower().replace('m', '')) * 1000000)
                    else: # Assume bps if no suffix
                        audio_bitrate_bps_for_calc = int(_final_audio_bitrate_str_for_calc)
                except ValueError as e_parse_audio_br:
                    LOGGER.error(f"Target Size Mode: Error parsing determined audio bitrate '{_final_audio_bitrate_str_for_calc}': {e_parse_audio_br}. Using fallback 128kbps for calculation.") # Use LOGGER
                    audio_bitrate_bps_for_calc = 128 * 1000
                    # Update the actual audio settings if they were problematic
                    convert_abit = "128k" # This will be used by the audio encoding part later
                    if convert_acodec.lower() == "copy": convert_acodec = _default_forced_audio_codec # This will be used by audio encoding part


                # Consider number of audio channels for audio_total_bits if needed, but FFmpeg handles this.
                # For simplicity, we use the single audio_bitrate_bps_for_calc.
                audio_total_bits_for_file = audio_bitrate_bps_for_calc * file_duration

                # Estimate overhead (muxing, metadata, etc.) - e.g., 2-5% of target size
                # This is a rough estimate and can vary.
                overhead_factor = 0.03 # 3% overhead
                estimated_overhead_bits = target_total_bits * overhead_factor

                remaining_bits_for_video = target_total_bits - audio_total_bits_for_file - estimated_overhead_bits

                if remaining_bits_for_video > 0:
                    calculated_video_bitrate_bps = int(remaining_bits_for_video / file_duration)
                    # Ensure a minimum video bitrate (e.g., 100kbps) to avoid issues
                    min_video_bitrate_bps = 100 * 1000
                    calculated_video_bitrate_bps = max(calculated_video_bitrate_bps, min_video_bitrate_bps)
                    calculated_video_bitrate_str = f"{calculated_video_bitrate_bps // 1000}k" # Convert to kbps string

                    LOGGER.info(f"Target Size Mode: Calculated target video bitrate: {calculated_video_bitrate_str}") # Use LOGGER
                    LOGGER.info(f"Target Size Mode: Audio will be: '{_final_audio_codec_for_calc}' at '{_final_audio_bitrate_str_for_calc}' (used for calculation).") # Use LOGGER
                    use_calculated_abr_for_video = True
                else:
                    LOGGER.warning(f"Target Size Mode: Target file size {target_size_mb}MB is too small for the video duration ({file_duration}s) and determined audio bitrate '{_final_audio_bitrate_str_for_calc}'. Video will use standard rate control settings from user.") # Use LOGGER
                    use_calculated_abr_for_video = False

            elif use_target_size and target_size_mb > 0 and file_duration <= 0:
                LOGGER.warning("Target Size Mode: Cannot determine video duration. Target file size feature disabled for this conversion.") # Use LOGGER
            elif use_target_size and target_size_mb <= 0:
                LOGGER.info("Target Size Mode: Disabled by user (Target MB is 0 or less).") # Use LOGGER
            # --- End of Target File Size Logic ---
# END OF MODIFIED BLOCK

            # --- Start of VFBITMOD-update Command Logic ---
            # Video Encoding Part
            if convert_encode == 'Video' or convert_encode == 'Video Audio [Both]':
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

            else: # Only Audio encode or no video encode
                command+=['-c:v', 'copy']

# START OF MODIFIED BLOCK
            # Audio Encoding Part - Respect Target Size Mode decisions for audio
            if convert_encode == 'Audio' or convert_encode == 'Video Audio [Both]':
                _actual_audio_codec_to_use = convert_acodec
                _actual_audio_bitrate_to_use = convert_abit

                if use_target_size and target_size_mb > 0 and file_duration > 0:
                    # Use the potentially overridden audio settings from target size calculation
                    _actual_audio_codec_to_use = _final_audio_codec_for_calc # From target size logic
                    _actual_audio_bitrate_to_use = _final_audio_bitrate_str_for_calc # From target size logic
                    LOGGER.info(f"Target Size Mode: Applying audio codec '{_actual_audio_codec_to_use}' and bitrate '{_actual_audio_bitrate_to_use}' for FFmpeg.") # Use LOGGER


                if _actual_audio_codec_to_use.lower() == 'copy' and not (use_target_size and target_size_mb > 0 and file_duration > 0) : # only copy if not overridden by target size
                    command += ['-c:a', 'copy']
                else:
                    # Audio Codec
                    if _actual_audio_codec_to_use.lower()=='opus':
                        codec = 'libopus'
                    elif _actual_audio_codec_to_use.lower()=='dd':
                        codec = 'ac3'
                    elif _actual_audio_codec_to_use.lower()=='ddp':
                        codec = 'eac3'
                    else: # Default AAC or user-specified if not copy
                        codec = 'aac'
                    command += ['-c:a', codec]

                    # Audio Bitrate (only if custom is enabled or set by target size)
                    if _actual_audio_bitrate_to_use: # This will be set if use_abit is true OR by target_size logic
                        command += ['-b:a', f'{str(_actual_audio_bitrate_to_use)}']

                # Audio Channels (always apply user's choice unless it was 'copy' and overridden)
                if convert_achannel.lower() != "copy": # Corrected: was user_settings_convert.get('audio', {}).get('achannel', '2')
                    command += ['-ac', f'{str(convert_achannel)}']
                # If convert_achannel is 'copy' AND target size mode forced re-encode, FFmpeg will pick channels.
                # If convert_achannel is 'copy' AND audio is copied, then channels are copied.
            else: # No audio encode (video only or copy all)
                command+= ['-c:a', 'copy']
# END OF MODIFIED BLOCK

            # Common Settings
            if convert_map:
                command+=['-map','0:v?',
                                            '-map',f'{str(process_status.amap_options)}?',
                                            "-map", "0:s?"]
            if convert_copysub:
                command+= ["-c:s", "copy"]

            convert_use_queue_size = get_data()[process_status.user_id]['convert']['use_queue_size']
            if convert_use_queue_size:
                convert_queue_size = get_data()[process_status.user_id]['convert']['queue_size']
                command+= ['-max_muxing_queue_size', f'{str(convert_queue_size)}']
            if convert_sync:
                command+= ['-vsync', '1', '-async', '-1']

# START OF MODIFIED BLOCK
            # Apply metadata if user has it enabled
            if apply_user_metadata_convert:
                LOGGER.info(f"CONVERT: Applying custom metadata. User text: '{user_global_metadata_text_convert}'")
                if user_global_metadata_text_convert: # Only if text is not empty
                    command.extend(['-metadata', f'title={user_global_metadata_text_convert}'])
                    command.extend(['-metadata', f'author={user_global_metadata_text_convert}'])
                    command.extend(['-metadata', f'comment={user_global_metadata_text_convert}'])
                    command.extend(['-metadata:s:v:0', f'title={user_global_metadata_text_convert}'])
                    command.extend(['-metadata:s:a', f'title={user_global_metadata_text_convert}'])
                    if convert_copysub: # Apply to subtitle titles only if copying subtitles
                        command.extend(['-metadata:s:s', f'title={user_global_metadata_text_convert}'])

                command.extend(['-metadata', 'encoded_by=[ BashAFK ~ TG_Eliteflix_Official ]'])
                command.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
                command.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
                LOGGER.info("CONVERT: Applied fixed metadata: encoded_by, description, telegram tags.")
# END OF MODIFIED BLOCK

# Highlighted change: Apply preset only if not VP9
            if convert_encoder != 'VP9':
                command+= ['-preset', convert_preset]
# End of highlighted change
            command+= ['-y', f"{output_file}"]
            # --- End of VFBITMOD-update Command Logic ---

            return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.hardmux:
# START OF MODIFIED BLOCK
        user_settings_hm = get_data()[process_status.user_id]
        apply_user_metadata_hm = user_settings_hm.get('custom_metadata', False)
        user_global_metadata_text_hm = user_settings_hm.get('metadata', "VideoFlux Default Title")
# END OF MODIFIED BLOCK
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
        command+= ['-vf', f"subtitles='{sub_loc}'",
                                    '-map','0:v',
                                    '-map',f'{str(process_status.amap_options)}']
        if hardmux_encode_video:
                encoder = get_data()[process_status.user_id]['hardmux']['encoder']
                if encoder=='libx265':
                        command += ['-vcodec','libx265', '-vtag', 'hvc1', '-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset]
                else:
                        command += ['-vcodec','libx264', '-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset]
                # HIGHLIGHTED CHANGE START: Ensure audio is copied when video is encoded for hardmux, as per comment intention
                command += ['-c:a','copy']
                # HIGHLIGHTED CHANGE END
        else: # If not encoding video, copy audio. If encoding video, audio will be re-encoded by default unless -c:a copy is added.
              # For hardmux, usually audio is copied if video is re-encoded with subtitles.
              # If video is also copied (hardmux_encode_video=False), then audio must be copied.
            command += ['-c:a','copy'] # Ensure audio is copied if video is not re-encoded or if user expects audio copy
        hardmux_sync = get_data()[process_status.user_id]['hardmux']['sync']
        hardmux_use_queue_size = get_data()[process_status.user_id]['hardmux']['use_queue_size']
        if hardmux_use_queue_size:
                hardmux_queue_size = get_data()[process_status.user_id]['hardmux']['queue_size']
                command+= ['-max_muxing_queue_size', f'{str(hardmux_queue_size)}']
        if hardmux_sync:
            command+= ['-vsync', '1', '-async', '-1']
# START OF MODIFIED BLOCK
        if apply_user_metadata_hm:
            LOGGER.info(f"HARDMUX: Applying custom metadata. User text: '{user_global_metadata_text_hm}'")
            if user_global_metadata_text_hm:
                command.extend(['-metadata', f'title={user_global_metadata_text_hm}'])
                command.extend(['-metadata', f'author={user_global_metadata_text_hm}'])
                command.extend(['-metadata', f'comment={user_global_metadata_text_hm}'])
                command.extend(['-metadata:s:v:0', f'title={user_global_metadata_text_hm}'])
                command.extend(['-metadata:s:a', f'title={user_global_metadata_text_hm}'])
                # No subtitle stream titles for hardmux as they are burned in
            command.extend(['-metadata', 'encoded_by=[ BashAFK ~ TG_Eliteflix_Official ]'])
            command.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
            command.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
            LOGGER.info("HARDMUX: Applied fixed metadata tags.")
# END OF MODIFIED BLOCK
        command += ["-y", f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.changeMetadata:
# START OF MODIFIED BLOCK
        # For /changemetadata, we primarily use its own specific logic for stream metadata.
        # However, we can still add the fixed global tags if custom_metadata is on.
        user_settings_cmd = get_data()[process_status.user_id]
        apply_user_metadata_cmd = user_settings_cmd.get('custom_metadata', False)
        user_global_metadata_text_cmd = user_settings_cmd.get('metadata', "VideoFlux Default Title") # User's main metadata text
# END OF MODIFIED BLOCK
        create_direc(f"{process_status.dir}/metadata/")
        log_file = f"{process_status.dir}/metadata/metadata_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/metadata/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        custom_metadata = process_status.custom_metadata # This is the specific stream metadata from /changemetadata command
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}'] # Reverted zender -> ffmpeg
        if custom_metadata: # Apply specific stream changes from the command first
            for m in custom_metadata:
                command+=m
# START OF MODIFIED BLOCK
        # Then, if global custom_metadata is on, apply the main file title from user's text
        # and the fixed tags. Author/comment from user's global text can also be added.
        if apply_user_metadata_cmd:
            LOGGER.info(f"CHANGEMETADATA: Applying global and fixed metadata. User text: '{user_global_metadata_text_cmd}'")
            if user_global_metadata_text_cmd:
                command.extend(['-metadata', f'title={user_global_metadata_text_cmd}']) # Main file title
                command.extend(['-metadata', f'author={user_global_metadata_text_cmd}'])
                command.extend(['-metadata', f'comment={user_global_metadata_text_cmd}'])
            command.extend(['-metadata', 'encoded_by=[ BashAFK ~ TG_Eliteflix_Official ]'])
            command.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
            command.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
            LOGGER.info("CHANGEMETADATA: Applied fixed metadata tags.")
        else: # If global custom_metadata is OFF, VideoFlux's original /changemetadata still sets a global title
              # using the 'metadata' field. This was the old behavior.
            original_vf_global_title = get_data()[process_status.user_id]['metadata']
            command += ['-metadata', f"title={original_vf_global_title}"]
# END OF MODIFIED BLOCK
        command += ["-map", "0", "-c", "copy", '-y', f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.changeindex:
# START OF MODIFIED BLOCK
        # For /changeindex, metadata is usually not the primary focus, but we can add
        # the main file title and fixed tags if custom_metadata is on.
        user_settings_ci = get_data()[process_status.user_id]
        apply_user_metadata_ci = user_settings_ci.get('custom_metadata', False)
        user_global_metadata_text_ci = user_settings_ci.get('metadata', "VideoFlux Default Title")
# END OF MODIFIED BLOCK
        create_direc(f"{process_status.dir}/index/")
        log_file = f"{process_status.dir}/index/index_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/index/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}', '-map', '0:v?'] + process_status.custom_index # Reverted zender -> ffmpeg
# START OF MODIFIED BLOCK
        if apply_user_metadata_ci:
            LOGGER.info(f"CHANGEINDEX: Applying global and fixed metadata. User text: '{user_global_metadata_text_ci}'")
            if user_global_metadata_text_ci:
                command.extend(['-metadata', f'title={user_global_metadata_text_ci}'])
                command.extend(['-metadata', f'author={user_global_metadata_text_ci}'])
                command.extend(['-metadata', f'comment={user_global_metadata_text_ci}'])
            command.extend(['-metadata', 'encoded_by=[ BashAFK ~ TG_Eliteflix_Official ]'])
            command.extend(['-metadata', 'description=Visit TG-@Eliteflix_Official'])
            command.extend(['-metadata', 'telegram=Downloaded From @Eliteflix_Official'])
            LOGGER.info("CHANGEINDEX: Applied fixed metadata tags.")
# END OF MODIFIED BLOCK
        command += ["-c", "copy", '-y', f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration

# --- END OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Commands.py ---
