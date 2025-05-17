import os
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in .env file or environment variables.")
    print("Please create a .env file with GOOGLE_API_KEY='your_api_key_here'")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)
try:
    gemini_model = genai.GenerativeModel('gemini-1.5-pro')
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    print("Please ensure your API key is valid and has access to the Gemini model.")
    exit()

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScycJV-Viw6vqKdTCUIfLa0CrswzwszAnnurHRr9ySSzsuxYw/viewform"
NUM_ENTRIES = 2
PROBABILITY_GEMINI_SUGGESTION = 0.6

def get_random_location():
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", 
              "Kolkata", "Pune", "Jaipur", "Lucknow", "Ahmedabad"]
    return random.choice(cities)

def get_random_awareness():
    return random.choice(["Yes", "No"])

def get_random_hear_about():
    options = ["Advertisement", "Word of mouth", "Dealer/ Distributor", "Other"]
    if random.random() < 0.1:
        return "**other_option**", f"CustomSource{random.randint(1,100)}"
    return random.choice(options), None

def get_random_seen_product():
    return random.choice(["Yes", "No"])

def get_random_cement_type():
    options = ["OPC ( Ordinary Portland Cement)", "PPC ( Portland Pozzolona Cement)", 
               "PSC ( Portland Slag Cement)", "White Cement", "Other"]
    if random.random() < 0.1:
        return "**other_option**", f"CustomType{random.randint(1,100)}"
    return random.choice(options), None

def get_random_satisfaction():
    return random.choice(["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"])

def get_random_purchase_source():
    return random.choice(["Direct from manufacturer", "Authorized dealer", "Local retailer", "Online platform"])

def get_random_purchase_factor():
    return random.choice(["Price", "Quality", "Brand reputation", "Availability"])

def get_random_purchase_frequency():
    return random.choice(["Weekly", "Monthly", "Quarterly", "Rarely"])

def get_random_brand_comparison():
    return random.choice(["Always", "Sometimes", "Rarely", "Never"])

def get_random_other_brands():
    brands = ["UltraTech", "ACC", "Ambuja", "Dalmia"]
    return random.sample(brands, random.randint(1, len(brands)))

def get_random_pricing_perception():
    return random.choice(["Very high", "Reasonable", "Competitive", "Low"])

def get_random_communication_opinion():
    return random.choice(["Yes", "No", "Not sure"])

def get_random_recommendation():
    return random.choice(["Yes", "No", "Maybe"])

def select_radio_button(driver, question_text_partial, option_value):
    try:
        # First try finding by aria-label
        try:
            radio_xpath = f"//div[@role='radio' and @aria-label='{option_value}']"
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, radio_xpath))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", element)
            time.sleep(0.5)
            return
        except:
            pass

        # Fallback to original method
        question_block_xpath = f"//div[@role='listitem'][.//*[contains(text(), '{question_text_partial}')]]"
        question_block = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, question_block_xpath))
        
        radio_button_xpath = f".//div[@role='radio'][@data-value='{option_value}']"
        element = WebDriverWait(question_block, 10).until(
            EC.element_to_be_clickable((By.XPATH, radio_button_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(0.5)
    except Exception as e:
        print(f"Error selecting radio button '{option_value}' for question containing '{question_text_partial}': {e}")
        driver.save_screenshot(f"error_radio_{question_text_partial.replace(' ', '_')[:20]}_{option_value}.png")
        raise

def select_checkboxes(driver, question_text_partial, option_values):
    try:
        question_block_xpath = f"//div[@role='listitem'][.//*[contains(text(), '{question_text_partial}')]]"
        question_block = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, question_block_xpath)))
        
        for option_value in option_values:
            checkbox_xpath = f".//div[@role='checkbox'][@data-value='{option_value}']"
            element = WebDriverWait(question_block, 10).until(
                EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
            time.sleep(0.3)
            if element.get_attribute("aria-checked") == "false":
                driver.execute_script("arguments[0].click();", element)
                time.sleep(0.3)
    except Exception as e:
        print(f"Error selecting checkbox '{option_values}' for question '{question_text_partial}': {e}")
        driver.save_screenshot(f"error_checkbox_{question_text_partial.replace(' ', '_')[:20]}.png")
        raise

def fill_text_input(driver, question_text_partial, text_to_fill, is_other_field=False):
    try:
        question_block_xpath = f"//div[@role='listitem'][.//*[contains(text(), '{question_text_partial}')]]"
        question_block = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, question_block_xpath)))

        if "suggestions for improving" in question_text_partial.lower():
            input_element = WebDriverWait(question_block, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//textarea")))
        elif is_other_field:
            input_element = WebDriverWait(question_block, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//div[contains(@class,'zfdaxb')]//input[@type='text']")))
        else:
            input_element = WebDriverWait(question_block, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//input[@type='text']")))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", input_element)
        time.sleep(0.3)
        input_element.clear()
        input_element.send_keys(text_to_fill)
        time.sleep(0.3)
    except Exception as e:
        print(f"Error filling text input for question '{question_text_partial}' (is_other={is_other_field}): {e}")
        driver.save_screenshot(f"error_text_input_{question_text_partial.replace(' ', '_')[:20]}.png")
        raise

def generate_gemini_suggestion(form_data):
    prompt_parts = [
        "Based on the following survey responses about Shree Cement, provide a 1-2 sentence suggestion for improving their products or services. Be concise, constructive, and directly address potential improvements.",
        "Relevant responses from one survey participant:",
        f"- Awareness of brand: {form_data.get('awareness', 'N/A')}",
        f"- How heard about: {form_data.get('hear_about_value', 'N/A')}",
        f"- Seen product in 12 months: {form_data.get('seen_product', 'N/A')}",
        f"- Cement type used: {form_data.get('cement_type_value', 'N/A')}",
        f"- Satisfaction with availability: {form_data.get('availability_satisfaction', 'N/A')}",
        f"- Purchase factors: {form_data.get('purchase_factor', 'N/A')}",
        f"- Pricing perception: {form_data.get('pricing_perception', 'N/A')}",
        f"- Would recommend: {form_data.get('recommendation', 'N/A')}",
    ]

    prompt = "\n".join(prompt_parts) + "\n\nSuggestion:"
    try:
        response = gemini_model.generate_content(prompt)
        suggestion = response.text.strip().replace("*", "").replace("\n", " ")
        if suggestion and not suggestion.endswith(('.', '!', '?')):
            suggestion += "."
        return suggestion if suggestion else "Improving distribution channels and brand awareness campaigns could help reach more customers."
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Focus on improving product availability and competitive pricing strategies."

def fill_form(driver, entry_data):
    try:
        driver.get(FORM_URL)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XXPATH, "//div[@role='listitem']")))
        time.sleep(random.uniform(2.5, 4))
        
        # Fill location
        fill_text_input(driver, "Location/city", entry_data["location"])
        
        # Q1: Awareness
        select_radio_button(driver, "Are you aware of Shree cement as brand", entry_data["awareness"])
        
        # Q2: How heard about
        if entry_data["hear_about_value"] == "**other_option**":
            select_radio_button(driver, "How do you first hear hear about Shree cement", "Other")
            fill_text_input(driver, "How do you first hear hear about Shree cement", entry_data["hear_about_other_text"], is_other_field=True)
        else:
            select_radio_button(driver, "How do you first hear hear about Shree cement", entry_data["hear_about_value"])
        
        # Q3: Seen product
        select_radio_button(driver, "Have you seen shree cement product in past 12 months", entry_data["seen_product"])
        
        # Q4: Cement type
        if entry_data["cement_type_value"] == "**other_option**":
            select_radio_button(driver, "which type of cement do you most frequently used", "Other")
            fill_text_input(driver, "which type of cement do you most frequently used", entry_data["cement_type_other_text"], is_other_field=True)
        else:
            select_radio_button(driver, "which type of cement do you most frequently used", entry_data["cement_type_value"])
        
        # Q5: Availability satisfaction
        select_radio_button(driver, "How satisfied are you with the availability of Shree Cement in your area", entry_data["availability_satisfaction"])
        
        # Q6: Purchase source
        select_radio_button(driver, "From where do you usually purchase cement", entry_data["purchase_source"])
        
        # Q7: Purchase factor
        select_radio_button(driver, "What is the most important factor in your cement purchase decision", entry_data["purchase_factor"])
        
        # Q8: Purchase frequency
        select_radio_button(driver, "How frequently do you purchase cement", entry_data["purchase_frequency"])
        
        # Q9: Brand comparison
        select_radio_button(driver, "Do you compare Shree Cement with other brands before making a purchase", entry_data["brand_comparison"])
        
        # Q10: Other brands
        select_checkboxes(driver, "Which other cement brands do you consider or use", entry_data["other_brands"])
        
        # Q11: Pricing perception
        select_radio_button(driver, "What is your perception of Shree Cement's pricing", entry_data["pricing_perception"])
        
        # Q12: Communication opinion
        select_radio_button(driver, "Do you feel Shree Cement communicates well through advertising and promotions", entry_data["communication_opinion"])
        
        # Q13: Recommendation
        select_radio_button(driver, "Would you recommend Shree Cement to others", entry_data["recommendation"])
        
        # Q14: Suggestions
        if entry_data.get("make_gemini_suggestion"):
            print("Generating Gemini suggestion for this entry...")
            suggestion = generate_gemini_suggestion(entry_data)
            entry_data["suggestion_text"] = suggestion
        
        if entry_data.get("suggestion_text"):
            fill_text_input(driver, "Any suggestions for improving Shree Cement's products or services", entry_data["suggestion_text"])
        elif entry_data.get("force_fill_suggestion_if_empty_and_required"):
            fill_text_input(driver, "Any suggestions for improving Shree Cement's products or services", "No specific suggestions at this time.")
        
        # Submit form
        submit_button_xpath = "//div[@role='button']//span[text()='Submit']"
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", submit_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", submit_button)

        WebDriverWait(driver, 30).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Your response has been recorded')]")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Submit another response')]"))
            ))
        print(f"Form submitted successfully for entry from: {entry_data['location']}")
    except Exception as e:
        print(f"Error filling form: {e}")
        driver.save_screenshot("form_fill_error.png")
        raise

if __name__ == "__main__":
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    options.add_argument("--window-size=1920,1200")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    for i in range(NUM_ENTRIES):
        print(f"\n--- Submitting Entry {i+1}/{NUM_ENTRIES} ---")
        current_driver = None
        try:
            current_driver = webdriver.Chrome(service=service, options=options)
            entry_data = {}

            # Generate random responses for each question
            entry_data["location"] = get_random_location()
            entry_data["awareness"] = get_random_awareness()
            
            hear_about_val, hear_about_other = get_random_hear_about()
            entry_data["hear_about_value"] = hear_about_val
            entry_data["hear_about_other_text"] = hear_about_other
            
            entry_data["seen_product"] = get_random_seen_product()
            
            cement_type_val, cement_type_other = get_random_cement_type()
            entry_data["cement_type_value"] = cement_type_val
            entry_data["cement_type_other_text"] = cement_type_other
            
            entry_data["availability_satisfaction"] = get_random_satisfaction()
            entry_data["purchase_source"] = get_random_purchase_source()
            entry_data["purchase_factor"] = get_random_purchase_factor()
            entry_data["purchase_frequency"] = get_random_purchase_frequency()
            entry_data["brand_comparison"] = get_random_brand_comparison()
            entry_data["other_brands"] = get_random_other_brands()
            entry_data["pricing_perception"] = get_random_pricing_perception()
            entry_data["communication_opinion"] = get_random_communication_opinion()
            entry_data["recommendation"] = get_random_recommendation()
            
            entry_data["make_gemini_suggestion"] = (random.random() < PROBABILITY_GEMINI_SUGGESTION)
            entry_data["suggestion_text"] = ""
            entry_data["force_fill_suggestion_if_empty_and_required"] = True

            fill_form(current_driver, entry_data)
            time.sleep(random.uniform(2.5, 4.5))

        except Exception as e:
            print(f"FATAL ERROR during form submission {i+1}: {e}")
            if current_driver:
                try:
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    current_driver.save_screenshot(f"fatal_error_submission_{i+1}_{timestamp}.png")
                    print(f"Saved screenshot: fatal_error_submission_{i+1}_{timestamp}.png")
                except Exception as e_screen:
                    print(f"Could not save screenshot/source after fatal error: {e_screen}")
        finally:
            if current_driver:
                current_driver.quit()
                time.sleep(1)  # Add small delay between instances

    print(f"\n--- Completed {NUM_ENTRIES} submissions ---")