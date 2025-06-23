FROM python:3.12

WORKDIR /app

# Set timezone to UTC
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update package lists and install dependencies in a single layer
RUN apt-get update && apt-get install -y \
    wget \
    chromium \
    chromium-driver \
    xvfb \
    x11-utils \
    x11-xserver-utils \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libappindicator3-1 \
    libnspr4 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome binary path environment variable
ENV SB_CHROME_BINARY_PATH=/usr/bin/chromium

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyAutoGUI explicitly for SeleniumBase UC mode
RUN pip3 install --no-cache-dir pyautogui==0.9.54

# Set up XVirtual Frame Buffer for headless operation
ENV DISPLAY=:99
ENV XVFB_SIZE=1920x1080x24

# Copy project files
COPY . .

# Set environment variables for SeleniumBase
ENV SB_DRIVER_DIR=/app/.seleniumbase/drivers

ENV SB_CHROME_NO_SANDBOX     "--no-sandbox"
ENV SB_CHROME_DISABLE_GPU    "--disable-gpu"
ENV SB_CHROME_DISABLE_DEV_SHM_USAGE "--disable-dev-shm-usage"

# Create directory for SeleniumBase drivers
RUN mkdir -p /app/.seleniumbase/drivers

# Start xvfb and run the application
CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & python run_scrapers_parallel.py"]