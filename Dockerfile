FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
# Install basic dependencies + tools needed to extract the static build
RUN apt -qq update && \
    apt -qq install -y --no-install-recommends wget unzip p7zip-full curl busybox aria2 xz-utils && \
    rm -rf /var/lib/apt/lists/*

# --- START: Install Static FFmpeg with libsvtav1 ---
ARG FFMPEG_VERSION=6.1.1
ARG TARGETPLATFORM
# Determine architecture for download URL
RUN case ${TARGETPLATFORM} in \
         "linux/amd64") ARCH=amd64 ;; \
         "linux/arm64") ARCH=arm64 ;; \
         *) echo "Unsupported architecture: ${TARGETPLATFORM}"; exit 1 ;; \
    esac && \
    FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-${FFMPEG_VERSION}-${ARCH}-static.tar.xz" && \
    echo "Downloading FFmpeg from ${FFMPEG_URL}" && \
    # Download FFmpeg static build
    wget -q ${FFMPEG_URL} -O ffmpeg.tar.xz && \
    # Create directory for extraction
    mkdir /ffmpeg-static && \
    # Extract FFmpeg
    tar -xf ffmpeg.tar.xz -C /ffmpeg-static --strip-components=1 && \
    # Copy ffmpeg and ffprobe to /usr/local/bin (which is usually in PATH)
    cp /ffmpeg-static/ffmpeg /usr/local/bin/ && \
    cp /ffmpeg-static/ffprobe /usr/local/bin/ && \
    # Make them executable
    chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe && \
    # Clean up downloaded file and extracted folder
    rm ffmpeg.tar.xz && \
    rm -rf /ffmpeg-static && \
    # Verify installation (optional but good)
    ffmpeg -version
# --- END: Install Static FFmpeg ---

COPY . /app
WORKDIR /app
RUN chmod 777 /app

RUN wget https://rclone.org/install.sh
RUN chmod 777 ./install.sh
RUN bash install.sh

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PORT=8000
EXPOSE 8000

CMD sh start.sh
