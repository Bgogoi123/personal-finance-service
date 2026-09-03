# An official lightweight Python Image.
FROM python:3.14-slim

# Setting the working directory inside the Container.
WORKDIR /app

# Copy the requirements.txt file to cache dependencies.
COPY requirements.txt .

# Install Python Dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file.
COPY main.py .

#  Copy the entire src folder.
COPY src/ ./src/

# Tell Docker which port the FastAPI app runs on.
EXPOSE 8000

# Command to run the FastAPI code using Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]