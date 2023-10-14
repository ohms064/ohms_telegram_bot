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

ENV TZ="America/Mexico_City" 

# command to run on container start
CMD [ "python", "./telegram_bot.py" ]