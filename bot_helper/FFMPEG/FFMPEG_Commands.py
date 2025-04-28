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
            merge_map = get_data()[process_status.user_id]['merge']['map']
            merge_fix_blank = get_data()[process_status.user_id]['merge']['fix_blank']
            # Highlighted change: Get the new setting
            merge_fix_timestamps = get_data()[process_status.user_id]['merge'].get('fix_timestamps', False) # Use .get() for safety
            # End of highlighted change

            create_direc(f"{process_status.dir}/merge/")
            log_file = f"{process_status.dir}/merge/merge_logs_{process_status.process_id}.txt"
            infile_names = ""
            file_duration =0
            for dwfile_loc in process_status.send_files:
                infile_names += f"file '{str(dwfile_loc)}'\n"
                file_duration += get_video_duration(dwfile_loc) # Note: This duration might still be based on individual files
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
                                        "-safe", "0"]
            if merge_fix_blank:
                command += ['-segment_time_metadata', '1']
            command+=["-i", f'{str(input_file)}']
            if merge_fix_blank:
                command += ['-vf', 'select=concatdec_select', '-af', 'aselect=concatdec_select,aresample=async=1']
            if merge_map:
                command+=['-map','0']

            # Highlighted change: Conditional -c copy based on the new setting
            if not merge_fix_blank: # Only consider -c copy if fix_blank is False
                if not merge_fix_timestamps: # Add -c copy only if fix_timestamps is also False (default, fast mode)
                    command+= ["-c", "copy"]
                else:
                    # If fixing timestamps (no global -c copy), explicitly copy subtitles
                    command += ["-c:s", "copy"] # Ensure subtitles are copied
            else:
                 # If fix_blank is True, -c copy is already omitted by its logic,
                 # but we might still want to ensure subtitle copy here too if needed.
                 command += ["-c:s", "copy"] # Ensure subtitles are copied even with fix_blank
            # End of highlighted change

            # Added metadata from VFBITMOD-update
            custom_metadata_title = get_data()[process_status.user_id]['metadata']
            command += ['-metadata', f"title={custom_metadata_title}", '-metadata:s:v', f"title={custom_metadata_title}", '-metadata:s:a', f"title={custom_metadata_title}", '-metadata:s:s', f"title={custom_metadata_title}"]
            # End of Added metadata
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
                command += ['-c:v','copy', '-c:a', 'copy'] # Explicitly copy V/A if not encoding

        command += ["-c:s", f"{get_data()[process_status.user_id]['softmux']['sub_codec']}", "-y", f"{output_file}"] # Keep subtitle codec setting

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
# End of highlighted change
            # --- End of VFBITMOD-update Integration ---

            # Highlighted change: Get advanced encoding settings
            adv_settings = get_data().get(process_status.user_id, {}).get('advanced_encoding', {})
            # End of highlighted change

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

            # --- Start of VFBITMOD-update Command Logic ---
            # Video Encoding Part
            if convert_encode == 'Video' or convert_encode == 'Video Audio [Both]':
                # Resolution Scaling
                if convert_quality=='480p [720x360]':
                    command+=['-vf', 'scale=720:360']
                elif convert_quality=='480p [720x480]':
                    command+=['-vf', 'scale=720:480']
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
                using_x265 = False # Flag to check if x265 is used
                if convert_encoder=='HEVC':
                    command+= ['-vcodec','libx265','-vtag', 'hvc1']
                    using_x265 = True
                else: # H.264
                    command+= ['-vcodec','libx264']

                # Highlighted change: Construct and add x265/x264 params
                # Get common values using .get() with defaults from adv_settings
                me = adv_settings.get('me', 'hex')
                b_adapt = adv_settings.get('b_adapt', '2')
                bframes = adv_settings.get('bframes', '4')
                aq_mode = adv_settings.get('aq_mode', '2')
                threads = adv_settings.get('threads', '0') # 0 = auto
                frame_threads = adv_settings.get('frame_threads', '0') # 0 = auto
                slices = adv_settings.get('slices', '0') # 0 = auto

                if using_x265:
                    x265_params = []
                    cutree = adv_settings.get('cutree', True) # x265 specific

                    x265_params.append(f"me={me}")
                    x265_params.append(f"b-adapt={b_adapt}")
                    # Corrected parameter name and added check for '0'
                    x265_params.append(f"bframes={bframes}")
                    x265_params.append(f"aq-mode={aq_mode}")
                    x265_params.append(f"cutree={'1' if cutree else '0'}")
                    if threads != '0': # Only add if not auto
                        x265_params.append(f"pools={threads}") # x265 uses pools
                    if frame_threads != '0': # Only add if not auto
                         x265_params.append(f"frame-threads={frame_threads}")
                    if slices != '0': # Only add if not auto
                         x265_params.append(f"slices={slices}")
                    # WPP is usually handled automatically based on threads, omit direct control

                    if x265_params: # Only add if list is not empty
                        command += ['-x265-params', ":".join(x265_params)]
                else: # libx264
                    # Construct x264 params (Note: names might differ slightly)
                    x264_params = []
                    # Map common params (some might not exist or have different names/values in x264)
                    # x264 doesn't have a direct 'me' setting like x265, 'subme' is related but different
                    # x264 uses b_adapt differently (0, 1, 2)
                    x264_params.append(f"b-adapt={b_adapt}")
                    # x264 uses lookahead differently - Added check for '0'
                    # if lookahead != '0': # REMOVED lookahead param
                    #     x264_params.append(f"rc-lookahead={lookahead}") # REMOVED lookahead param
                    x264_params.append(f"bframes={bframes}")
                    # x264 aq-mode (0, 1, 2)
                    x264_aq_mode = aq_mode if aq_mode in ['0', '1', '2'] else '1' # Default to 1 if x265 value is 3
                    x264_params.append(f"aq-mode={x264_aq_mode}")
                    # x264 doesn't have cutree
                    if threads != '0':
                        x264_params.append(f"threads={threads}") # x264 uses threads
                    # x264 doesn't have frame-threads in the same way
                    if slices != '0':
                        x264_params.append(f"slices={slices}")

                    if x264_params:
                        command += ['-x264-params', ":".join(x264_params)]
                # End of highlighted change

# Highlighted change: Add tune setting if not 'None'
                # Tune Setting
                if video_tune != 'None':
                    command += ['-tune', video_tune]
# End of highlighted change

                # Rate Control (CRF, VBR, ABR, or CBR)
                if convert_type=='CRF' and convert_crf is not None:
                    command+= ['-crf', f'{str(convert_crf)}']
                elif convert_type=='VBR' and convert_vbr is not None:
                    command+= ['-b:v', f'{str(convert_vbr)}']
                elif convert_type=='ABR' and convert_abr is not None:
                    command+= ['-b:v', f'{str(convert_abr)}'] # ABR (1-pass) uses -b:v
                # Highlighted change: Added CBR handling
                elif convert_type=='CBR' and convert_cbr is not None:
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
                # If type is set but value is None (not enabled), FFmpeg might use defaults or error.
                # Consider adding a default CRF/VBR if type is selected but value isn't enabled.
                elif convert_type=='CRF': # Default CRF if enabled but no value set
                     command+= ['-crf', '23'] # Example default
                elif convert_type=='VBR': # Default VBR if enabled but no value set
                     command+= ['-b:v', '1500k'] # Example default
                elif convert_type=='ABR': # Default ABR if enabled but no value set
                     command+= ['-b:v', '1500k'] # Example default
                # Highlighted change: Added CBR default fallback
                elif convert_type=='CBR': # Default CBR if enabled but no value set
                     command += ['-b:v', '1500k', '-minrate', '1500k', '-maxrate', '1500k', '-bufsize', '3000k'] # Example default

            else: # Only Audio encode or no video encode
                command+=['-c:v', 'copy']

            # Audio Encoding Part
            if convert_encode == 'Audio' or convert_encode == 'Video Audio [Both]':
                # Audio Codec
                if convert_acodec=='OPUS':
                    codec = 'libopus'
                elif convert_acodec=='DD':
                    codec = 'ac3'
                elif convert_acodec=='DDP':
                    codec = 'eac3'
                else: # Default AAC
                    codec = 'aac'
                command += ['-c:a', codec]

                # Audio Bitrate (only if custom is enabled)
                if convert_abit is not None:
                    command += ['-b:a', f'{str(convert_abit)}']

                # Audio Channels
                command += ['-ac', f'{str(convert_achannel)}']
            else: # No audio encode
                command+= ['-c:a', 'copy']

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

            command+= ['-preset', convert_preset]
            command+= ['-y', f"{output_file}"]
            # --- End of VFBITMOD-update Command Logic ---

            return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.hardmux:
        hardmux_preset =  get_data()[process_status.user_id]['hardmux']['preset']
        hardmux_crf = get_data()[process_status.user_id]['hardmux']['crf']
        hardmux_encode_video = get_data()[process_status.user_id]['hardmux']['encode_video']
        # Highlighted change: Get advanced encoding settings
        adv_settings = get_data().get(process_status.user_id, {}).get('advanced_encoding', {})
        # End of highlighted change
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
                # Highlighted change: Get common advanced params for hardmux
                me = adv_settings.get('me', 'hex')
                b_adapt = adv_settings.get('b_adapt', '2')
                # lookahead = adv_settings.get('lookahead', '20') # REMOVED lookahead retrieval
                bframes = adv_settings.get('bframes', '4')
                aq_mode = adv_settings.get('aq_mode', '2')
                threads = adv_settings.get('threads', '0')
                frame_threads = adv_settings.get('frame_threads', '0')
                slices = adv_settings.get('slices', '0')
                # End of highlighted change

                if encoder=='libx265':
                        command += ['-vcodec','libx265', '-vtag', 'hvc1']
                        # Highlighted change: Construct and add x265 params for hardmux
                        x265_params = []
                        cutree = adv_settings.get('cutree', True) # x265 specific

                        x265_params.append(f"me={me}")
                        x265_params.append(f"b-adapt={b_adapt}")
                        # Corrected parameter name and added check for '0'
                        # if lookahead != '0': # REMOVED lookahead param
                        #     x265_params.append(f"lookahead={lookahead}") # REMOVED lookahead param
                        x265_params.append(f"bframes={bframes}")
                        x265_params.append(f"aq-mode={aq_mode}")
                        x265_params.append(f"cutree={'1' if cutree else '0'}")
                        if threads != '0':
                            x265_params.append(f"pools={threads}") # x265 uses pools
                        if frame_threads != '0':
                             x265_params.append(f"frame-threads={frame_threads}")
                        if slices != '0':
                             x265_params.append(f"slices={slices}")

                        if x265_params:
                            command += ['-x265-params', ":".join(x265_params)]
                        # End of highlighted change
                        command += ['-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset] # Add CRF and preset after params
                else: # libx264
                        command += ['-vcodec','libx264']
                        # Highlighted change: Construct and add x264 params for hardmux
                        x264_params = []
                        x264_params.append(f"b-adapt={b_adapt}")
                        # Added check for '0'
                        # if lookahead != '0': # REMOVED lookahead param
                        #     x264_params.append(f"rc-lookahead={lookahead}") # REMOVED lookahead param
                        x264_params.append(f"bframes={bframes}")
                        x264_aq_mode = aq_mode if aq_mode in ['0', '1', '2'] else '1'
                        x264_params.append(f"aq-mode={x264_aq_mode}")
                        if threads != '0':
                            x264_params.append(f"threads={threads}")
                        if slices != '0':
                            x264_params.append(f"slices={slices}")

                        if x264_params:
                            command += ['-x264-params', ":".join(x264_params)]
                        # End of highlighted change
                        command += ['-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset] # Add CRF and preset
        else: # If not encoding video, copy audio
                command += ['-c:a','copy']

        hardmux_sync = get_data()[process_status.user_id]['hardmux']['sync']
        hardmux_use_queue_size = get_data()[process_status.user_id]['hardmux']['use_queue_size']
        if hardmux_use_queue_size:
                hardmux_queue_size = get_data()[process_status.user_id]['hardmux']['queue_size']
                command+= ['-max_muxing_queue_size', f'{str(hardmux_queue_size)}']
        if hardmux_sync:
            command+= ['-vsync', '1', '-async', '-1']
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
        for m in custom_metadata:
            command+=m
        # Added global title metadata from VFBITMOD-update
        custom_metadata_title = get_data()[process_status.user_id]['metadata']
        command += ['-metadata', f"title={custom_metadata_title}"]
        # End of Added global title metadata
        command += ["-map", "0", "-c", "copy", '-y', f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration


    elif process_status.process_type==Names.changeindex:
        create_direc(f"{process_status.dir}/index/")
        log_file = f"{process_status.dir}/index/index_logs_{process_status.process_id}.txt"
        input_file = f'{str(process_status.send_files[-1])}'
        output_file = f"{process_status.dir}/index/{get_output_name(process_status)}"
        file_duration = get_video_duration(input_file)
        command = ['ffmpeg','-hide_banner', '-progress', f"{log_file}", '-i', f'{str(input_file)}', '-map', '0:v?'] + process_status.custom_index # Reverted zender -> ffmpeg
        command += ["-c", "copy", '-y', f"{output_file}"]
        return command, log_file, input_file, output_file, file_duration

# --- END OF FILE VideoFlux-Re-master/bot_helper/FFMPEG/FFMPEG_Commands.py ---
