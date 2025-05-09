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
            if merge_map:
                command+=['-map','0']
            if not merge_fix_blank:
                command+= ["-c", "copy"]
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
        command+= input_sub # Add new subtitle input files
# START OF MODIFIED BLOCK ###################################################
        # Mapping streams: new subtitles, then original video, audio, original subtitles, and original attachments
        command += sub_map # Maps new subtitles (e.g., -map 1:0, -map 2:0 for inputs from input_sub)
        command += ['-map','0:v?'] # Map original video stream from input 0 (optional)
        command += ['-map',f'{str(process_status.amap_options)}?'] # Map original audio streams from input 0 (e.g., 0:a, optional)
        command += ['-map','0:s?'] # Map original subtitle streams from input 0 (optional)
        command += ['-map','0:t?'] # Map original attachment streams from input 0 (e.g., fonts, optional)
        command += ['-disposition:s:0','default'] # Set the first output subtitle stream as default

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
                # If video is encoded, explicitly copy audio and attachments
                command += ['-c:a', 'copy']
                command += ['-c:t', 'copy']
        else:
                # If not encoding video, copy all mapped streams (video, audio, original subs, attachments)
                command += ['-c','copy']

        # Set codec for all subtitle streams (original and new ones that were mapped)
        command += ["-c:s", f"{get_data()[process_status.user_id]['softmux']['sub_codec']}"]
        command += ["-y", f"{output_file}"]
# END OF MODIFIED BLOCK #####################################################
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

                # Rate Control (CRF, VBR, ABR, or CBR)
                if convert_type=='CRF' and convert_crf is not None:
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

# Highlighted change: Apply preset only if not VP9
            if convert_encoder != 'VP9':
                command+= ['-preset', convert_preset]
# End of highlighted change
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
        command+= ['-vf', f"subtitles='{sub_loc}'",
                                    '-map','0:v',
                                    '-map',f'{str(process_status.amap_options)}']
        if hardmux_encode_video:
                encoder = get_data()[process_status.user_id]['hardmux']['encoder']
                if encoder=='libx265':
                        command += ['-vcodec','libx265', '-vtag', 'hvc1', '-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset]
                else:
                        command += ['-vcodec','libx264', '-crf', f'{str(hardmux_crf)}', '-preset', hardmux_preset]
        else:
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
