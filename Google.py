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
    exit()

genai.configure(api_key=GOOGLE_API_KEY)
try:
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    exit()

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScycJV-Viw6vqKdTCUIfLa0CrswzwszAnnurHRr9ySSzsuxYw/viewform"
NUM_ENTRIES = 5
PROBABILITY_GEMINI_SUGGESTION = 0.5

# Answer generation functions
def get_random_city():
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", 
             "Kolkata", "Pune", "Jaipur", "Ahmedabad", "Surat"]
    return random.choice(cities)

def get_random_awareness():
    return random.choice(["Yes", "No"])

def get_random_hearing_method():
    methods = ["Advertisement", "Word of mouth", "Dealer/ Distributor"]
    if random.random() < 0.1:
        return "Other", f"Other source {random.randint(1,100)}"
    return random.choice(methods), None

def get_random_product_sighting():
    return random.choice(["Yes", "No"])

def get_random_cement_type():
    types = ["OPC ( Ordinary Portland Cement)", "PPC ( Portland Pozzolona Cement)",
            "PSC ( Portland Slag Cement)", "White Cement"]
    if random.random() < 0.1:
        return "Other", f"Other type {random.randint(1,100)}"
    return random.choice(types), None

def get_random_satisfaction():
    return random.choice(["Very satisfied", "Satisfied", "Neutral", 
                         "Dissatisfied", "Very dissatisfied"])

def get_random_purchase_source():
    return random.choice(["Direct from manufacturer", "Authorized dealer",
                         "Local retailer", "Online platform"])

def get_random_purchase_factor():
    return random.choice(["Price", "Quality", "Brand reputation", "Availability"])

def get_random_purchase_frequency():
    return random.choice(["Weekly", "Monthly", "Quarterly", "Rarely"])

def get_random_brand_comparison():
    return random.choice(["Always", "Sometimes", "Rarely", "Never"])

def get_random_other_brands():
    # Since this is actually a radio button question, we'll return a single choice
    brands = ["UltraTech", "ACC", "Ambuja", "Dalmia", "Shree Cement"]
    return random.choice(brands)

def get_random_pricing_perception():
    return random.choice(["Very high", "Reasonable", "Competitive", "Low"])

def get_random_ad_communication():
    return random.choice(["Yes", "No", "Not sure"])

def get_random_recommendation():
    return random.choice(["Yes", "No", "Maybe"])

def select_radio_button(driver, question_text_partial, option_value):
    try:
        # First try to find the question block
        # Handle single quotes in the question text by using concat() in XPath
        if "'" in question_text_partial:
            question_text_partial = question_text_partial.replace("'", "\\'")
        question_block_xpath = f"//div[@role='listitem'][.//*[contains(text(), '{question_text_partial}')]]"
        
        question_block = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, question_block_xpath)))
        
        # Scroll the question into view first
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", question_block)
        time.sleep(0.5)
        
        # Try different ways to find the radio button
        try:
            # First try by data-value attribute
            radio_xpath = f".//div[@role='radio'][@data-value='{option_value}']"
            element = WebDriverWait(question_block, 5).until(
                EC.element_to_be_clickable((By.XPATH, radio_xpath)))
        except:
            # If that fails, try by the option text with more flexible matching
            try:
                radio_xpath = f".//div[@role='radio']//span[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{option_value.lower()}')]/ancestor::div[@role='radio']"
                element = WebDriverWait(question_block, 5).until(
                    EC.element_to_be_clickable((By.XPATH, radio_xpath)))
            except:
                # As a last resort, try to find by position if the options are in a consistent order
                options = question_block.find_elements(By.XPATH, ".//div[@role='radio']")
                if options:
                    for opt in options:
                        if option_value.lower() in opt.text.lower():
                            element = opt
                            break
                    else:
                        raise Exception(f"Option '{option_value}' not found in radio buttons")
                else:
                    raise Exception(f"Could not locate radio button for option '{option_value}'")
            
        # Click using JavaScript to avoid interception
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(0.5)
        
        # Verify selection was successful
        if element.get_attribute("aria-checked") != "true":
            raise Exception(f"Radio button selection failed for {option_value}")
            
    except Exception as e:
        print(f"Error selecting radio button '{option_value}' for question containing '{question_text_partial}': {e}")
        driver.save_screenshot(f"error_radio_{question_text_partial.replace(' ', '_')[:20]}_{option_value}.png")
        raise

def fill_text_input(driver, question_text_partial, text_to_fill, is_other_field=False):
    try:
        # Special handling for Location/city field
        if "Location/city" in question_text_partial:
            # Try to find the input field directly by its type and aria-label
            try:
                input_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='text' and contains(@aria-label, 'Location/city')]")))
            except:
                # Alternative approach if the above doesn't work
                question_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(., 'Location/city')]"))
                )
                input_element = question_div.find_element(By.XPATH, ".//input[@type='text']")
        elif is_other_field:
            # For "Other" text fields
            question_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(., '{question_text_partial}')]"))
            )
            input_element = question_div.find_element(By.XPATH, ".//input[@type='text']")
        else:
            # Existing logic for other fields
            try:
                input_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//input[contains(@aria-label, '{question_text_partial}')]"))
                )
            except:
                try:
                    input_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//textarea[contains(@aria-label, '{question_text_partial}')]"))
                    )
                except:
                    question_div = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[contains(., '{question_text_partial}')]"))
                    )
                    input_element = question_div.find_element(By.XPATH, ".//input | .//textarea")

        # Scroll and interact with the element
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", input_element)
        time.sleep(0.5)
        
        # Clear existing value
        input_element.clear()
        time.sleep(0.2)
        
        # Type the text
        input_element.send_keys(text_to_fill)
        time.sleep(0.5)
            
    except Exception as e:
        print(f"Error filling text input for question '{question_text_partial}': {e}")
        driver.save_screenshot(f"error_text_input_{question_text_partial.replace(' ', '_')[:20]}.png")
        raise

def generate_gemini_suggestion(form_data):
    prompt = f"""Based on these survey responses about Shree Cement:
    - City: {form_data.get('city', 'N/A')}
    - Brand Awareness: {form_data.get('awareness', 'N/A')}
    - Product Sighting: {form_data.get('product_sighting', 'N/A')}
    - Satisfaction: {form_data.get('satisfaction', 'N/A')}
    - Purchase Factors: {form_data.get('purchase_factor', 'N/A')}
    - Pricing Perception: {form_data.get('pricing_perception', 'N/A')}
    
    Provide a brief suggestion (1-2 sentences) for Shree Cement to improve their products/services:"""
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return "Focus on improving customer engagement and product availability."

def fill_form(driver, entry_data):
    driver.get(FORM_URL)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//form")))
    time.sleep(2)  # Additional wait for form to fully load

    # Location/City
    fill_text_input(driver, "Location/city", entry_data["city"])
    time.sleep(1)
    
    # Brand Awareness
    select_radio_button(driver, "Are you aware of Shree cement as brand", entry_data["awareness"])
    time.sleep(1)
    
    # Hearing method
    method, other_text = entry_data["hearing_method"]
    select_radio_button(driver, "How do you first hear hear about Shree cement", method)
    if other_text:
        time.sleep(1)
        fill_text_input(driver, "How do you first hear hear about Shree cement", other_text, is_other_field=True)
    time.sleep(1)
    
    # Product sighting
    select_radio_button(driver, "Have you seen shree cement product in past 12 months", entry_data["product_sighting"])
    time.sleep(1)
    
    # Cement type
    cement_type, type_other = entry_data["cement_type"]
    try:
        select_radio_button(driver, "which type of cement do you most frequently used", cement_type)
        if type_other:
            time.sleep(1)
            fill_text_input(driver, "which type of cement do you most frequently used", type_other, is_other_field=True)
    except Exception as e:
        print(f"Error handling cement type question: {e}")
        # Fallback to a default option
        select_radio_button(driver, "which type of cement do you most frequently used", "OPC ( Ordinary Portland Cement)")
    time.sleep(1)
    
    # Satisfaction
    select_radio_button(driver, "How satisfied are you with the availability", entry_data["satisfaction"])
    time.sleep(1)
    
    # Purchase source
    select_radio_button(driver, "From where do you usually purchase cement", entry_data["purchase_source"])
    time.sleep(1)
    
    # Purchase factor
    select_radio_button(driver, "What is the most important factor in your cement purchase decision", entry_data["purchase_factor"])
    time.sleep(1)
    
    # Purchase frequency
    select_radio_button(driver, "How frequently do you purchase cement", entry_data["purchase_frequency"])
    time.sleep(1)
    
    # Brand comparison
    select_radio_button(driver, "Do you compare Shree Cement with other brands", entry_data["brand_comparison"])
    time.sleep(1)
    
    try:
        select_radio_button(driver, "Which other cement brands do you consider", entry_data["other_brands"])
    except:
        # Fallback to a more specific selector if the general one fails
        select_radio_button(driver, "other cement brands", entry_data["other_brands"])
    time.sleep(1)
    
    # Pricing perception - Special handling for this question
    try:
        # First try with simplified question text
        select_radio_button(driver, "What is your perception of Shree Cement pricing", entry_data["pricing_perception"])
    except:
        try:
            # Try alternative approach by finding all radio groups and selecting the right one
            all_radio_groups = driver.find_elements(By.XPATH, "//div[@role='listitem']")
            for group in all_radio_groups:
                if "perception" in group.text.lower() and "pricing" in group.text.lower():
                    options = group.find_elements(By.XPATH, ".//div[@role='radio']")
                    for opt in options:
                        if entry_data["pricing_perception"].lower() in opt.text.lower():
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", opt)
                            time.sleep(0.3)
                            driver.execute_script("arguments[0].click();", opt)
                            time.sleep(0.5)
                            break
                    break
        except Exception as e:
            print(f"Error handling pricing perception question: {e}")
            driver.save_screenshot("pricing_perception_error.png")
    
    time.sleep(1)
    
    # Ad communication
    select_radio_button(driver, "Do you feel Shree Cement communicates well through advertising", entry_data["ad_communication"])
    time.sleep(1)
    
    # Recommendation
    select_radio_button(driver, "Would you recommend Shree Cement to others", entry_data["recommendation"])
    time.sleep(1)
    
    # Suggestions - Improved handling with proper scrolling
    if entry_data.get("make_gemini_suggestion"):
        try:
            entry_data["suggestion_text"] = generate_gemini_suggestion(entry_data)
            print(f"Generated suggestion: {entry_data['suggestion_text']}")
        except Exception as e:
            print(f"Error generating Gemini suggestion: {e}")
            entry_data["suggestion_text"] = "Focus on improving quality and customer service"
    
    if entry_data.get("suggestion_text"):
        try:
            # First locate the suggestions question using more specific text
            suggestions_xpath = "//div[contains(., 'Any suggestions for improving') and contains(@role, 'listitem')]"
            suggestions_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, suggestions_xpath))
            )
            
            # Scroll to the suggestions field smoothly and wait
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'nearest'
                });
            """, suggestions_div)
            time.sleep(1)  # Wait for scrolling to complete
            
            # Find the input field within the suggestions div
            input_fields = suggestions_div.find_elements(By.XPATH, ".//textarea | .//input[@type='text']")
            
            if not input_fields:
                raise Exception("Could not find suggestions input field")
                
            input_field = input_fields[0]
            
            # Clear and fill the field
            driver.execute_script("arguments[0].value = '';", input_field)
            time.sleep(0.3)
            input_field.send_keys(entry_data["suggestion_text"])
            
            # Verify the text was entered
            entered_text = input_field.get_attribute('value')
            if entry_data["suggestion_text"] not in entered_text:
                print(f"Expected: {entry_data['suggestion_text']}")
                print(f"Actual: {entered_text}")
                raise Exception("Suggestion text not properly entered")
                
        except Exception as e:
            print(f"Error filling suggestions: {e}")
            driver.save_screenshot("suggestion_error.png")

    time.sleep(1)
    
    # Submit form
    submit_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='button'][.//span[text()='Submit']]")))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", submit_button)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", submit_button)
    time.sleep(2)

if __name__ == "__main__":
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    for i in range(NUM_ENTRIES):
        print(f"Submitting entry {i+1}/{NUM_ENTRIES}")
        driver = None
        try:
            driver = webdriver.Chrome(service=service, options=options)
            entry_data = {
                "city": get_random_city(),
                "awareness": get_random_awareness(),
                "hearing_method": get_random_hearing_method(),
                "product_sighting": get_random_product_sighting(),
                "cement_type": get_random_cement_type(),
                "satisfaction": get_random_satisfaction(),
                "purchase_source": get_random_purchase_source(),
                "purchase_factor": get_random_purchase_factor(),
                "purchase_frequency": get_random_purchase_frequency(),
                "brand_comparison": get_random_brand_comparison(),
                "other_brands": get_random_other_brands(),
                "pricing_perception": get_random_pricing_perception(),
                "ad_communication": get_random_ad_communication(),
                "recommendation": get_random_recommendation(),
                "make_gemini_suggestion": random.random() < PROBABILITY_GEMINI_SUGGESTION
            }
            
            fill_form(driver, entry_data)
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"Error submitting entry {i+1}: {e}")
            if driver:
                driver.save_screenshot(f"error_entry_{i+1}.png")
        finally:
            if driver:
                driver.quit()

    print("All submissions completed!")