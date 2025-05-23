# Use the public AWS Lambda Python image as the base image
FROM public.ecr.aws/lambda/python:3.12

# Copy the Python dependencies file and install the dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app module directly into /var/task/
COPY src/app_name/ /var/task/app_name/

# Set the working directory to /var/task/
WORKDIR /var/task/

# Define the command to run the Lambda function handler
CMD ["app_name.__main__.handler"]