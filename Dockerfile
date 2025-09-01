FROM python:3.9

ENV DEBIAN_FRONTEND=noninteractive
RUN apt -qq update \
    # Enable 'contrib' and 'non-free' repositories
    && sed -i 's/ main$/ main contrib non-free/' /etc/apt/sources.list \
    # Update apt cache again to include packages from the newly enabled repositories
    && apt -qq update \
    && apt -qq install -y wget unzip p7zip-full curl busybox aria2 build-essential yasm nasm pkg-config libx264-dev libx265-dev libvpx-dev libfdk-aac-dev libopus-dev libass-dev \
    && wget https://ffmpeg.org/releases/ffmpeg-7.1.1.tar.bz2 \
    && tar xjf ffmpeg-7.1.1.tar.bz2 \
    && cd ffmpeg-7.1.1 \
    && ./configure --enable-gpl --enable-nonfree --enable-libx264 --enable-libx265 --enable-libvpx --enable-libfdk-aac --enable-libopus --enable-libass \
    && make -j$(nproc) \
    && make install \
    && cd .. \
    && rm -rf ffmpeg-7.1.1* \
    # Clean up apt caches to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN chmod 777 /app

RUN wget https://rclone.org/install.sh \
    && chmod 777 ./install.sh \
    && bash install.sh

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "start.sh"]
