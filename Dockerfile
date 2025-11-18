# Use the official lightweight Python image based on Debian
FROM python:3.12.9

# Set the working directory
WORKDIR /xkdc-daily

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application
CMD ["sh", "-c", "python src/scraper.py && python src/update_readme.py"]
