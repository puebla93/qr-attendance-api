FROM python:3.8
LABEL Javier Puebla "jpuebla1993@gmail.com"

# Setting these enviroment variable to ensure that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# Creating root directory for our project in the container
RUN mkdir /attendace_service

# Setting the working directory to /attendace_service
WORKDIR /attendace_service

# Copy the current directory contents into the container at /attendace_service
ADD . /attendace_service/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
