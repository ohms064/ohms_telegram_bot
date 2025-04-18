# set base image (host OS)
FROM python:3.12.0-bookworm

# set the working directory in the container
WORKDIR /app

# copy the dependencies file to the working directory
COPY Info/requirements.txt requirements.txt

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY Modules /app/Modules
COPY TelegramModules /app/TelegramModules
COPY telegram_bot.py /app/telegram_bot.py
COPY Info/firebase_key.json /app/Info/firebase_key.json
COPY Info/api_keys.json /app/Info/api_keys.json

ENV TZ="America/Mexico_City" 

# command to run on container start
CMD [ "python", "telegram_bot.py" ]