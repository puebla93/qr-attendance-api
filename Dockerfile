FROM python:3.8
LABEL Javier Puebla "jpuebla1993@gmail.com"

# Setting these enviroment variable to ensure that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# Creating root directory for our project in the container
RUN mkdir /qr_attendace_api

# Setting the working directory to /api
WORKDIR /api

# Copy the current directory contents into the container at /api
ADD . /api/

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
