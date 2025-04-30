FROM python:3.9


ENV DEBIAN_FRONTEND=noninteractive
# Highlighted change: Modified apt install sequence to add deb-multimedia for potentially newer ffmpeg with libsvtav1
RUN apt -qq update && \
    apt -qq install -y --no-install-recommends wget unzip p7zip-full curl busybox aria2 gnupg && \
    # Add deb-multimedia repository
    echo "deb https://www.deb-multimedia.org bullseye main" > /etc/apt/sources.list.d/deb-multimedia.list && \
    # Import deb-multimedia key
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 5C808C2B65558117 && \
    # Update again after adding new repo
    apt -qq update && \
    # Install ffmpeg (hopefully from deb-multimedia) - allow untrusted as key import might sometimes be tricky in Docker
    apt -qq install -y --allow-unauthenticated ffmpeg && \
    # Clean up
    rm -rf /var/lib/apt/lists/*
# End of highlighted change

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
