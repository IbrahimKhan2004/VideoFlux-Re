FROM python:3.9


ENV DEBIAN_FRONTEND=noninteractive
RUN apt -qq update && apt -qq install -y wget unzip p7zip-full curl busybox aria2 libfontconfig1 libfreetype6 xz-utils
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && tar -xf ffmpeg-release-amd64-static.tar.xz && mv ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/ && mv ffmpeg-*-amd64-static/ffprobe /usr/local/bin/ && rm -rf ffmpeg-release-amd64-static.tar.xz ffmpeg-*-amd64-static

COPY . /app
WORKDIR /app
RUN chmod 777 /app

RUN wget https://rclone.org/install.sh
RUN chmod 777 ./install.sh
RUN bash install.sh

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PORT = 8080
EXPOSE 8080

CMD sh start.sh
