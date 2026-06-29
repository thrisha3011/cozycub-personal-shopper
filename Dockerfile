# Use the official Microsoft Playwright image that includes Python and browser dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set up the working directory inside the container
WORKDIR /app

# Copy your requirements file first to take advantage of caching layers
COPY requirements.txt .

# Install your Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port that Flask/Gunicorn will run on
EXPOSE 10000

# Run the app using Gunicorn bound to Render's dynamic port environment variable
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]