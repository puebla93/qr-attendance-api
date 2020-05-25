FROM python:3.8
LABEL Javier Puebla "jpuebla1993@gmail.com"

# Setting these enviroment variable to ensure that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# Creating root directory for our project in the container
RUN mkdir /attendance_api

# Setting the working directory to /attendance_api
WORKDIR /attendance_api

# Copy the current directory contents into the container at /attendance_api
ADD . /attendance_api/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
