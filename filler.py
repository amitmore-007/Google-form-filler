from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfEIxSgGvZ_vj-EZD5mr-2l4KE3xV4LR3gGw_ZcescMzPKvYA/viewform"

age_options = ['Below 18', '18-24', '25-34', '35-44', '45-54', '55+']
gender_options = ['Male', 'Female', 'Prefer not to say']
own_vehicle = ['Yes', 'No', 'Planning to buy soon']
vehicle_type = ['2-wheeler', 'EV 2-wheeler', '4-wheeler', 'EV 4-wheeler']
safety_features = [
    'Anti-lock Braking System (ABS)', 'Airbags', 'Electronic Stability Control (ESC)',
    'Advanced Driver Assistance Systems (ADAS)', 'Hill Hold Assist', 'Lane Keep Assist',
    'Blind Spot Detection', 'No idea about any'
]
importance = ['Not at all important', '1', '2', '3', '4', '5', 'Extremely important']
influencers = ['Price', 'Fuel efficiency', 'Brand', 'Safety features', 'Looks / Design', 'Resale value', 'Other']
essential_feature = ['ABS', 'Airbags', 'ADAS', 'ESC', 'Blind Spot Detection', 'Not sure']
accident_options = ['Yes', 'No', 'Prefer not to say']
yes_no_maybe = ['Yes', 'No', 'Maybe']
disable_feature_options = ['Yes', 'No', 'Not applicable']
conf_level = ['Never heard of them', '1', '2', '3', '4', '5', 'Very confident']
learn_sources = ['Dealership', 'YouTube / Online reviews', 'Friends/Relatives', 'Auto expos', 'Ads', 'I don’t research much']
ncap_check = ['Yes', 'No', 'Maybe']
agreement = ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree']

options = Options()
# options.add_argument("--headless")  # Optional: Run without UI
driver = webdriver.Chrome(options=options)

def choose(option_text):
    try:
        el = driver.find_element(By.XPATH, f"//*[text()[normalize-space()='{option_text}']]")
        driver.execute_script("arguments[0].click();", el)
        time.sleep(0.5)
    except Exception as e:
        print(f"[!] Could not select: '{option_text}' – {e}")

def fill_form():
    driver.get(form_url)
    time.sleep(2)

    choose(random.choice(age_options))
    choose(random.choice(gender_options))
    choose(random.choice(own_vehicle))
    choose(random.choice(vehicle_type))
    choose(random.choice(safety_features))
    choose(random.choice(importance))
    choose(random.choice(influencers))
    choose(random.choice(essential_feature))
    choose(random.choice(accident_options))
    choose(random.choice(yes_no_maybe))
    choose(random.choice(yes_no_maybe))
    choose(random.choice(disable_feature_options))
    choose(random.choice(yes_no_maybe))
    choose(random.choice(yes_no_maybe))
    choose(random.choice(conf_level))
    choose(random.choice(learn_sources))
    choose(random.choice(ncap_check))
    choose(random.choice(agreement))

    # Submit form
    try:
        submit_btn = driver.find_element(By.XPATH, '//span[contains(text(),"Submit")]')
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(3)
        print("✅ Form submitted.")

        # Confirmation check
        confirmation = driver.find_element(By.XPATH, '//*[contains(text(),"Your response has been recorded")]')
        if confirmation:
            print("✅ Confirmation: Response recorded.")
    except Exception as e:
        print("❌ Submit failed:", e)

# Submit multiple times
for i in range(1):
    print(f"\n=== Submitting form {i+1} ===")
    fill_form()
    time.sleep(3)


