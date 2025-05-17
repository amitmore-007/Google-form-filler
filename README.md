# 📝 Google Forms Auto Filler using Selenium

This Python script automatically fills out and submits a Google Form multiple times using Selenium. It's useful for testing, demoing form responses, or automating repetitive submissions.

---

## 🚀 Features

- Auto-fill Google Forms with custom responses.
- Submit the form multiple times based on user input.
- Uses Selenium WebDriver for browser automation.
- Configurable number of submissions and delays.

---


## 🔧 Requirements

- Python 3.x
- Google Chrome browser
- ChromeDriver (must match your Chrome version)

---

## 📦 Installation

1. Clone the repository


git clone  https://github.com/amitmore-007/Google-form-filler.git
l
Create a virtual environment (optional but recommended)

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

Install dependencies


pip install -r requirements.txt
Download ChromeDriver

Download the appropriate version from: https://sites.google.com/chromium.org/driver/

Place it in the project root or specify the path in the .env file.

⚙️ Configuration
Create a .env file in the root directory:

env

FORM_URL=https://docs.google.com/forms/d/e/your-form-id/viewform
CHROMEDRIVER_PATH=./chromedriver
NUM_SUBMISSIONS=10
You can adjust NUM_SUBMISSIONS or hardcode specific values inside the script if preferred.

▶️ Usage

python Google.py
The script will:

Open the Google Form in Chrome

Auto-fill each question with pre-defined answers

Submit the form repeatedly as specified

🛑 Disclaimer
This script is intended for educational and testing purposes only. Do not use it to spam or manipulate data, which violates Google’s terms of service.
