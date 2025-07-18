from openai import AzureOpenAI
from dotenv import load_dotenv
from crewai.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os

load_dotenv()

# FIXED: Correct parameter names for AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_API_BASE"),  # Changed from api_base
    api_version=os.getenv("AZURE_API_VERSION"),
    api_key=os.getenv("AZURE_API_KEY")
)

class CampaignTool(BaseTool):

    name: str = "campaign_tool"
    description: str = "Launches Edge and logs into IRIS Studio to create campaigns"

    def _run(self, input: str = "") -> str:  # FIXED: Added default value
        print(">>> CampaignTool _run called!")
        driver = None
        
        try:
            # Configure Edge browser options
            options = Options()
            options.add_argument("--start-maximized")

            # Driver path
            driver_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "drivers", "msedgedriver.exe")
            )
            if not os.path.exists(driver_path):
                return f"❌ Edge driver not found at path: {driver_path}"

            service = Service(driver_path)
            driver = webdriver.Edge(service=service, options=options)

            # Login Process
            driver.get("https://aka.ms/irisstudio")
            time.sleep(3)

            login_button = driver.find_element(By.TAG_NAME, "button")
            login_button.click()
            print("✅ Login button clicked.")
            time.sleep(5)

            try:
                
                checkbox_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='I have read and acknowledge this message.']/preceding::div[contains(@class,'ms-Checkbox-checkbox')][1]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox_box)
                driver.execute_script("arguments[0].click();", checkbox_box)
                print("✅ Checkbox ticked using label-based path.")
            except Exception as e:
                print(f"❌ Failed to tick checkbox: {e}")
            

            # Click Proceed
            try:
                proceed_button = driver.find_element(By.XPATH, "//button[contains(., 'Proceed')]")
                proceed_button.click()
                print("✅ 'Proceed' button clicked.")
                time.sleep(3)
            except Exception as e:
                suggestion = client.chat.completions.create(
                    messages = [
                        {"role":"user","content": f"Selenium failed with error: {str(e)}. Suggest retry logic or alt XPath."}
                    ],
                    model="gpt-4o",
                )
                print(suggestion.choices[0].message.content)

            # Navigate to Campaigns
            try:
                time.sleep(2)
                campaigns_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Campaigns')]")
                campaigns_button.click()
                print("✅ 'Campaigns' button clicked.")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Cannot click on campaigns button: {e}")
                # Try alternative campaigns button selector
                try:
                    campaigns_button = driver.find_element(By.XPATH, "//a[@href='/managecampaigns']")
                    campaigns_button.click()
                    print("✅ 'Campaigns' button clicked using href.")
                    time.sleep(2)
                except Exception as e2:
                    print(f"❌ Could not find campaigns button with any method: {e2}")
                    return f"❌ Could not find campaigns button: {e2}"

            
            try:
                time.sleep(2)
                create_campaign_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Create Campaign')]")
                create_campaign_button.click()
                print("✅ 'Create Campaign' button clicked.")
                time.sleep(5)
            except Exception as e:
                print(f"⚠ Could not find 'Create Campaign' button: {e}")
                return f"❌ Could not find 'Create Campaign' button: {e}"
       
            
            try:
                
                campaign_name_input = driver.find_element(By.XPATH, "//input[@placeholder='For example: eRFM engagement campaign to drive MAU increase']")
                campaign_name_input.clear()
                campaign_name_input.send_keys("Demo Campaign 2")
                print("✅ Campaign name entered using placeholder.")
                time.sleep(1)
            except Exception as e:
                print(f"⚠ Could not find campaign name input using placeholder: {e}")

            
            
            try:
                campaign_desc_input = driver.find_element(By.XPATH, "//textarea[@placeholder='Enter a brief description (max 400 char)']")
                campaign_desc_input.clear()
                campaign_desc_input.send_keys("Window 11 Upgrade Campaign - AI Generated Description")
                print("✅ Campaign description entered using placeholder.")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not find campaign description input using placeholder: {e}")

           
            try:
                
                owner_group_dropdown = driver.find_element(By.XPATH, "//span[contains(text(), 'Choose owner group')]")
                owner_group_dropdown.click()
                print("✅ Owner group dropdown opened.")
                time.sleep(2)

            
                try:
                        engineering_option = driver.find_element(By.XPATH, "//span[contains(@class, 'ms-Dropdown-optionText') and text()='E+D Engineering']")
                        engineering_option.click()
                        print("✅ E+D Engineering selected using alternative selector.")
                        time.sleep(2)
                except Exception as e:
                        print(f"⚠ Could not find E+D Engineering option: {e}")
                            
            except Exception as e:
                print(f"⚠ Could not find owner group dropdown: {e}")

            
            # Open the dropdown
                
            try:
               
                dropdown_label = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Choose line of business')]"))
                )
                driver.execute_script("arguments[0].click();", dropdown_label)
                time.sleep(1.5)  # give time for options to appear

                # Select the option
                option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ms-Dropdown-optionText') and text()='Consumer']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", option)
                driver.execute_script("arguments[0].click();", option)

            except Exception as e:
                print(f"⚠ Could not find or select line of business dropdown: {e}")
                return f"❌ Could not find or select line of business dropdown: {e}"

                  

            try:
               
                # product_dropdown = driver.find_element(By.XPATH, "//span[contains(text(), 'Choose product')]")
                product_dropdown = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Choose product')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", product_dropdown)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", product_dropdown)
                print("✅ product dropdown opened.")
                time.sleep(2)

                try:
                        product_option = driver.find_element(By.XPATH, "//span[contains(@class, 'ms-Dropdown-optionText') and text()='Windows']")
                        product_option.click()
                        print("✅ Windows selected using alternative selector.")
                        time.sleep(2)
                except Exception as e:
                        print(f"⚠ Could not find windows option: {e}")
                            
            except Exception as e:
                print(f"⚠ Could not find product dropdown: {e}")


            try:
    # Click the dropdown
                okr_dropdown_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'ms-Dropdown') and .//span[contains(text(),'Choose business goal')]]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", okr_dropdown_button)
                time.sleep(1)
                okr_dropdown_button.click()
                print("✅ OKR (business goal) dropdown opened.")
                time.sleep(1.5)

                # Trigger keyboard interaction to populate options (simulate down arrow key press)
                ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(1)

                # Try getting the options again
                options = driver.find_elements(By.XPATH, "//span[contains(@class,'ms-Dropdown-optionText')]")
                print(f"🧾 Found {len(options)} business goal options:")
                for opt in options:
                    print(f"➡️ '{opt.text}'")

                # If options found, click the first one
                if options:
                    driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", options[0])
                    driver.execute_script("arguments[0].click();", options[0])
                    print(f"✅ Business goal selected: {options[0].text}")
                else:
                    print("⚠ No options found in business goal dropdown after triggering interaction.")

            except Exception as e:
                print(f"❌ Could not handle OKR dropdown: {e}")

            

            try:
                time.sleep(2)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Create')]/ancestor::button"))
                )
                create_button = driver.find_element(By.XPATH, "//span[contains(text(),'Create')]/ancestor::button")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", create_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", create_button)
            except Exception as e:
                print(f"⚠ Could not find create button: {e}")

            try:
                time.sleep(2)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Create')]/ancestor::button"))
                )
                create_button = driver.find_element(By.XPATH, "//span[contains(text(),'Create')]/ancestor::button")
               
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", create_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", create_button)
                
                print("✅ Create button clicked.")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not find create button: {e}")
            # driver.get("https://portal.cpm.microsoft.com/managecampaigns/5179732") 

            try:
                time.sleep(5)
                add_line_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Add Line')]")
                add_line_button.click()
                print("✅ 'Add Line' button clicked.")
            except Exception as e:
                print(f"⚠ Could not find 'Add Line' button: {e}")
                return f"❌ Could not find 'Add Line' button: {e}"
            
            try: 
                time.sleep(2)  
                line_name_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter a name']")
                line_name_input.clear()
                line_name_input.send_keys("Windows 11 demo line 1")
                print("✅ Line name entered using placeholder.")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not find line name input using placeholder: {e}")

            try:
                time.sleep(2)
                outcome_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Choose an outcome') and contains(@class,'ms-Dropdown-title')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", outcome_dropdown)
                time.sleep(2)
                outcome_dropdown.click()
                print("✅ Outcome dropdown opened.")

                outcome_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ms-Dropdown-optionText') and text()='Windows Insider Program Usage']"))
                )
                outcome_option.click()
                print("✅ Outcome option selected.")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not find or select outcome dropdown: {e}")
                return f"❌ Could not find or select outcome dropdown: {e}"


            try:
                time.sleep(2)
                surface_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Choose a surface') and contains(@class,'ms-Dropdown-title')]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", surface_dropdown)
                time.sleep(1)
                surface_dropdown.click()
                print("✅ Surface dropdown opened.")
                time.sleep(1.5)

                option_text = "Game Pass ANH - iOS"
                # Wait for the option to be present and visible
                surface_option = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, f"//span[contains(@class, 'ms-Dropdown-optionText') and normalize-space(text())='{option_text}']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", surface_option)
                time.sleep(0.3)
                try:
                    surface_option.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", surface_option)
                print(f"✅ Surface option selected: {option_text}")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not find or select surface dropdown/option: {e}")
                return f"❌ Could not find or select surface dropdown/option: {e}"



            try:
                time.sleep(2)
                product_ring_dropdown = driver.find_element(By.XPATH, "//span[contains(text(), 'Choose a product ring')]")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", product_ring_dropdown)
                # product_ring_dropdown.click()
                driver.execute_script("arguments[0].click();", product_ring_dropdown)
                print("✅ Product ring dropdown opened.")
                time.sleep(2)
                try:
                    options = driver.find_elements(By.XPATH, "//span[contains(@class,'ms-Dropdown-optionText')]")
                    print("Dropdown options:")
                    for opt in options:
                        print(opt.text)
                    selfhost_option = driver.find_element(By.XPATH, "//span[contains(@class,'ms-Dropdown-optionText') and text()='SelfhostInternal']")
                    driver.execute_script("arguments[0].click();", selfhost_option)
                    print("✅ SelfhostInternal selected from product ring dropdown.")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠ Could not find SelfhostInternal option: {e}")
                    return f"❌ Could not find SelfhostInternal option: {e}"
            except Exception as e:
                print(f"⚠ Could not find product ring dropdown: {e}")
                return f"❌ Could not find product ring dropdown: {e}"


            



            try:
                time.sleep(2)
    
    # Click on the locale dropdown using the exact HTML structure
                locale_dropdown = driver.find_element(By.XPATH, "//span[contains(text(), 'Choose a locale')]")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", locale_dropdown)
                locale_dropdown.click()
                print("✅ Locale dropdown opened.")
                time.sleep(2)

        
                try:
        # Use the exact nested structure from your HTML
                        en_us_option = driver.find_element(
    By.XPATH,
    "//span[contains(@class,'ms-Dropdown-optionText') and normalize-space(text())='EN-US']"
)
                        en_us_option.click()
                        print("✅ EN-US selected from locale dropdown.")
                        time.sleep(2)
        
                except Exception as e:
                        print(f"⚠ Could not find EN-US option with exact selector: {e}")
            except Exception as e:
                    print(f"⚠ Could not find or select locale dropdown: {e}")
                    return f"❌ Could not find or select locale dropdown: {e}"


            try:
                time.sleep(2)
                end_date_label = driver.find_element(By.XPATH, "//label[contains(text(), 'End date')]")
                calendar_icon = end_date_label.find_element(
                    By.XPATH,
                    ".//following::i[@data-icon-name='Calendar' and contains(@class, 'ms-Icon')][1]"
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", calendar_icon)
                time.sleep(1)
                calendar_icon.click()
                print("✅ Calendar icon clicked - date picker opened.")
                time.sleep(2)
                try:
                    date_cells = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//td[contains(@class, 'dayCell-') and @role='gridcell']//button[contains(@class, 'dayButton-')]"))
                    )
                    print(f"📅 Found {len(date_cells)} available dates in calendar.")

                    target_date = "18, July, 2025"
                    clicked = False
                    for btn in date_cells:
                        try:
                            if btn.is_displayed() and btn.get_attribute("aria-label") == target_date:
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
                                driver.execute_script("arguments[0].click();", btn)
                                print(f"✅ Date selected: {target_date}")
                                clicked = True
                                time.sleep(2)
                                break
                        except Exception as click_error:
                            print(f"⚠ Could not click date: {click_error}")

                    if not clicked:
                        print(f"⚠ Could not find or select the date: {target_date}")
                        return f"❌ Could not select the date: {target_date}"
                except Exception as date_error:
                    print(f"⚠ Could not select date from calendar: {date_error}")

            except Exception as e:
                print(f"⚠ Could not find or select end date input: {e}")
                return f"❌ Could not find or select end date input: {e}"




            try:
                time.sleep(2)
                # focus_dropdown = driver.find_element(By.XPATH, "//span[contains(text(), 'Choose focus')]")
                focused_product_dropdown = driver.find_element(By.XPATH, "//span[contains(text(), 'Choose a focused product')]")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", focused_product_dropdown)
                focused_product_dropdown.click()
                print("✅ Focused product dropdown opened.")
                time.sleep(2)

                windows_options = WebDriverWait(driver,10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//span[text()='Windows']"))
                    )
                print(f"found {len(windows_options)} Windows options.")
                if len(windows_options) >=1:

                    driver.execute_script("arguments[0].click();", windows_options[0])
                    print("✅ Windows 1 selected.")
                    time.sleep(2)

                    nested_windows_options = WebDriverWait(driver,10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//span[contains(text(),'Windows')]"))
                    )
                    if len(nested_windows_options) > 1:
                        driver.execute_script("arguments[0].click();", nested_windows_options[1])
                        print("✅ Windows 2 selected.")
                        time.sleep(2)
                    else:
                        print("⚠ No second Windows option found.")
                else:
                    print("⚠ No Windows options found in focused product dropdown.")
                    return "❌ No Windows options found in focused product dropdown."
            except Exception as e:
                print(f"⚠ Could not find focused product dropdown: {e}")
                return f"❌ Could not find focused product dropdown: {e}"

            # Keep browser open for verification
            # driver.find_element(By.TAG_NAME, "body").click()  # Reset zoom level
            try:
                time.sleep(2)
                # Find the Create button by its label text
                create_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Create']/ancestor::button"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", create_button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", create_button)
                print("✅ Create button clicked.")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ Could not find or click Create button: {e}")
                return f"❌ Could not find or click Create button: {e}"
           




            print("✅ Campaign creation workflow completed successfully!")
            print("🔍 Browser will stay open for 15 seconds for verification...")
            time.sleep(15)
            
            return "✅ Successfully navigated to IRIS Studio, created campaign with name, description, owner group (E+D Engineering), line of business (Consumer), and OKR selection!"

        except Exception as e:
            print(f"❌ Error during automation process: {e}")
            return f"❌ Error during automation process: {e}"
        
        finally:
            # Clean up - close the browser
            if driver:
                try:
                    driver.quit()
                    print("🛑 Browser closed.")
                except:
                    print("⚠ Could not close browser properly.")

class NavigatorTool(BaseTool):

    name: str = "navigator_tool"
    description: str = "Launches Edge and logs into IRIS Studio"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open(os.path.join(os.path.dirname(__file__), "config.json"), 'r') as f:
            object.__setattr__(self, 'config', json.load(f))

    def _get_image_path(self, label_name):
                    # print("config called")
                    """Get full image path from config"""
                    base_dir = self.config["image_paths"]["base_directory"]
                    filename = self.config["image_paths"]["images"].get(label_name)
                    
                    if not filename:
                        print(f"⚠️ Image not found in config for label: {label_name}")
                        return None
                    
                    return os.path.join(base_dir, filename)
    
    def _generate_settings_with_ai(self):
        """Generate settings values using GPT-4o and update config.json"""
        print("🤖 Generating creative settings using GPT-4o...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at generating creative marketing content settings."
                    },
                    {
                        "role": "user", 
                        "content": """Generate values for these creative settings fields:

1. creative_name: A catchy, professional name for a Windows 11 upgrade creative campaign
2. ndup_id: A unique alphanumeric identifier (format: LETTERS_NUMBERS_NUMBERS)
3. layout_option: Choose from: layout_option must be exactly one of: LeftCenter, RightCenter, SinglePageNDUP (pick randomly).
4. tips: A helpful tip message for users (1-2 sentences)
5. learn_more: UI experiment enum for Learn More page
6. eula_page: UI experiment enum for EULA page experience
7. outro_page: UI experiment enum for Outro page design
8. decline_page: UI experiment enum for Decline page design
9. schedule_page: UI experiment enum for Schedule page design
10. loss aversion page: UI experiment enum for Loss Aversion page design
11. main_page: A short description of the main page content

Respond in this exact JSON format:
{
  "creative_name": "your_creative_name_here",
  "ndup_id": "your_ndup_id_here", 
  "layout_option": "your_layout_choice_here",
  "tips": "your_helpful_tip_here",
  "learn_more": "your_learn_more_variant_here",
  "eula_page": "your_eula_page_variant_here",
  "outro_page": "your_outro_page_variant_here",
  "decline_page": "your_decline_page_variant_here",
  "schedule_page": "your_schedule_page_variant_here",
  "loss_aversion_page": "your_loss_aversion_page_variant_here",
  "main_page": "your_main_page_description_here"
}

Only provide the JSON response, nothing else."""
                    }
                ],
max_tokens=200,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            print(f"🧠 GPT-4o response:\n{ai_response}")
            
            # Parse the AI response
            try:
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    ai_settings = json.loads(json_match.group())
                else:
                    ai_settings = json.loads(ai_response)
                print("✅ Successfully parsed AI-generated settings:")
                for key, value in ai_settings.items():
                    print(f"   {key}: {value}")
                
                return ai_settings
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse AI response: {e}")
                # return self._get_fallback_settings()

        except Exception as e:
            print(f"❌ Error calling GPT-4o: {e}")

    def _update_config_with_ai_settings(self):
        """Update config.json with AI-generated settings"""
        print("📝 Updating config.json with AI-generated settings...")
        
        new_settings = self._generate_settings_with_ai()
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Update settings section
            config["settings"].update(new_settings)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            object.__setattr__(self, 'config', config)  # Update instance config

            print("✅ Config.json updated with AI-generated settings!")

            # Update instance config
            object.__setattr__(self, 'config', config)
            return True
            
        except Exception as e:
            print(f"❌ Error updating config.json: {e}")
            return False

    def _run(self, input: dict) -> str:  # FIXED: Added default value
        print(">>> NavigatorTool _run called!")
        driver = None

        print("🤖 Generating creative settings with AI...")
        self._update_config_with_ai_settings()

        time.sleep(5)  # Allow time for config update
        
        
        try:
            # Configure Edge browser options
            options = Options()
            options.add_argument("--start-maximized")
            

            # Driver path
            driver_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..", "drivers", "msedgedriver.exe")
            )
            if not os.path.exists(driver_path):
                return f"❌ Edge driver not found at path: {driver_path}"

            service = Service(driver_path)
            driver = webdriver.Edge(service=service, options=options)

            # Login Process
            driver.get("https://aka.ms/irisstudio")
            time.sleep(3)

            login_button = driver.find_element(By.TAG_NAME, "button")
            login_button.click()
            print("✅ Login button clicked.")
            time.sleep(5)

            try:
                
                checkbox_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='I have read and acknowledge this message.']/preceding::div[contains(@class,'ms-Checkbox-checkbox')][1]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox_box)
                driver.execute_script("arguments[0].click();", checkbox_box)
                print("✅ Checkbox ticked using label-based path.")
            except Exception as e:
                print(f"❌ Failed to tick checkbox: {e}")
            

            # Click Proceed
            try:
                proceed_button = driver.find_element(By.XPATH, "//button[contains(., 'Proceed')]")
                proceed_button.click()
                print("✅ 'Proceed' button clicked.")
                time.sleep(3)
            except Exception as e:
                suggestion = client.chat.completions.create(
                    messages = [
                        {"role":"user","content": f"Selenium failed with error: {str(e)}. Suggest retry logic or alt XPath."}
                    ],
                    model="gpt-4o",
                )
                print(suggestion.choices[0].message.content)

            # Navigate to Creatives
            try:
                creatives_button = driver.find_element(By.XPATH, "//button[contains(., 'Creatives')]")
                creatives_button.click()
                print("✅ 'Creatives' button clicked.")
                time.sleep(2)

                # Create New Creative
                new_creative_button = driver.find_element(By.XPATH, "//button[contains(., 'New Creative')]")
                new_creative_button.click()
                print("✅ 'New Creative' button clicked.")
                time.sleep(2)

                # Fill Creative Name
                wait = WebDriverWait(driver, 5)
                name_input = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//input[contains(@placeholder,'Enter a name for your Creative')]"
                )))
                name_input.send_keys(self.config["settings"]["creative_name"])
                # name_input.send_keys("demo creative 1")
                time.sleep(1)

                if name_input.get_attribute('value') != self.config["settings"]["creative_name"]:
                    driver.execute_script("arguments[0].value = arguments[1];", name_input, self.config["settings"]["creative_name"])

                
                print("✅ Entered creative name.")
                time.sleep(1)


                try:
                    time.sleep(2)
                    surface_dropdown = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Select Creative template') and contains(@class,'ms-Dropdown-title')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", surface_dropdown)
                    time.sleep(1)
                    surface_dropdown.click()
                    print("✅ Surface dropdown opened.")
                    time.sleep(1.5)

                    option_text = "VB Nth Logon NDUP Lite"

                    # Type in the filter/search input to filter the dropdown options
                    filter_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Filter options']"))
                    )
                    filter_input.clear()
                    filter_input.send_keys(option_text)
                    print(f"✅ Typed '{option_text}' in filter box")
                    time.sleep(1.5)  # Wait for the dropdown to filter

                   
                    options = driver.find_elements(By.XPATH, "//span[contains(@class, 'ms-Dropdown-optionText')]")
                    print("Visible options after filter:", [opt.text.strip() for opt in options])
                    clicked = False
                    match_indices = [idx for idx, opt in enumerate(options) if opt.text.strip() == option_text and opt.is_displayed() and opt.is_enabled()]

                    if match_indices:
                        # Prefer the second match if it exists, else the first
                        idx = match_indices[1] if len(match_indices) > 1 else match_indices[0]
                        opt = options[idx]
                        print(f"Clicking option {idx}: '{opt.text.strip()}'")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", opt)
                        time.sleep(0.3)
                        try:
                            opt.click()
                            print(f"✅ Surface option selected (normal click): {option_text}")
                            clicked = True
                        except Exception as e:
                            print(f"⚠️ Normal click failed: {e}, trying JS click...")
                            try:
                                driver.execute_script("arguments[0].click();", opt)
                                print(f"✅ Surface option selected (JS click): {option_text}")
                                clicked = True
                            except Exception as e2:
                                print(f"⚠️ JS click also failed: {e2}")

                    if not clicked:
                        print(f"❌ Could not find or click the surface option: {option_text}")
                        return f"❌ Could not find or click the surface option: {option_text}"
                    time.sleep(2)



                except Exception as e:
                    print(f"⚠ Could not find or select surface dropdown/option: {e}")
                    return f"❌ Could not find or select surface dropdown/option: {e}"



                try:
                    time.sleep(2)
                    # Find the Generate Creative button by its label text
                    generate_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Generate Creative']/ancestor::button"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", generate_button)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", generate_button)
                    print("✅ Generate Creative button clicked.")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠ Could not find or click Generate Creative button: {e}")
                    return f"❌ Could not find or click Generate Creative button: {e}"

                time.sleep(5)
 
                self.fill_config_inputs(driver)

                print("Selecting page layout enum ")
                layout_dropdown = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//label[contains(text(),'Hero Page Layout Enum')]"))
                )
                dropdown_box = layout_dropdown.find_element(
                    By.XPATH, "following::span[contains(@class,'ms-Dropdown-title')][1]"
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", dropdown_box)
                time.sleep(1)
                driver.execute_script("arguments[0].click()", dropdown_box)
                print("✅ Clicked hero page dropdown")

                left_center_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class,'ms-Dropdown-optionText') and text()='{self.config['settings']['layout_option']}']"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", left_center_option)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", left_center_option)
                print("✅ Selected option")
                time.sleep(2)

            


                print("📸 Starting image uploads from configuration...")
                for label_name in self.config["image_paths"]["images"]:
                    image_path = self._get_image_path(label_name)
                    if image_path:
                        self._upload_image(driver, image_path, label_name)
                    else:
                        print(f"⚠️ Skipping {label_name} - image path not found")

            
                # Configure Locales  

                self._configure_locales(driver)

                # Generate AI content and upload CSV
                self._generate_and_upload_csv(driver)

                # Save Draft
                self.slow_scroll_page(driver)
                self._save_draft(driver)

                

            except Exception as e:
                suggestion = client.chat.completions.create(
                    messages = [
                        {"role":"user","content": f"Selenium failed with error: {str(e)}. Suggest retry logic or alt XPath."}
                    ],
                    model="gpt-4o",
                )
                print(suggestion.choices[0].message.content)
                print(f"❌ Error in automation flow: {e}")
                if driver:
                    driver.quit()
                return f"❌ Automation failed: {e}"

            print("✅ Automation complete, keeping browser open for 5 seconds...")
            time.sleep(5)
            driver.quit()
            return "✅ Completed creative creation flow successfully."

        except Exception as e:
            suggestion = client.chat.completions.create(
                    messages = [
                        {"role":"user","content": f"Selenium failed with error: {str(e)}. Suggest retry logic or alt XPath."}
                    ],
                    model="gpt-4o",
            )
            print(suggestion.choices[0].message.content)
            if driver:
                driver.quit()
            return f"❌ Navigation failed: {str(e)}"

    def _upload_image(self, driver, image_path, label_name):
        """Upload image to specified label field"""
        print(f"📸 Uploading image to '{label_name}'...")
        
        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False
        
        try:
            wait = WebDriverWait(driver, 5)
            
            # Find the label containing the specified text
            print(f"🔍 Looking for label: '{label_name}'")
            bg_label = wait.until(EC.presence_of_element_located((
                By.XPATH, f"//label[contains(text(),'{label_name}')]"
            )))
            driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", bg_label)
            time.sleep(1)
            print(f"✅ Found label: '{label_name}'")

            # Find the Upload Media button associated with this label
            print(f"🔍 Looking for Upload Media button for '{label_name}'")
            upload_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, f"//label[contains(text(),'{label_name}')]/following::span[text()='Upload Media'][1]"
            )))
            driver.execute_script("arguments[0].click();", upload_button)
            print(f"✅ Clicked Upload Media button for '{label_name}'")
            time.sleep(2)

            # Find file input and upload the image
            print(f"📂 Selecting file: {os.path.basename(image_path)}")
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            file_input.send_keys(image_path)
            print(f"✅ File selected: {os.path.basename(image_path)}")
            time.sleep(2)

            # Confirm upload
            print(f"⬆️ Confirming upload for '{label_name}'...")
            upload_confirm = wait.until(EC.element_to_be_clickable((
                By.XPATH, "//span[text()='Upload']/ancestor::button"
            )))
            driver.execute_script("arguments[0].click();", upload_confirm)
            print(f"✅ Image successfully uploaded to '{label_name}'")
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload image to '{label_name}': {str(e)}")
            return False

    def _configure_locales(self, driver):
        """Configure locale settings"""
        print("Configuring locales...")
        
        choose_locales_btn = driver.find_element(By.XPATH, "//span[contains(text(),'Choose Locales')]")
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", choose_locales_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", choose_locales_btn)
        print("✅ Choose Locales button clicked")
        time.sleep(2)

        filter_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Filter by name']"))
        )
        filter_input.clear()
        filter_input.send_keys("EN-US")
        print("✅ Typed EN-US in filter box")
        time.sleep(2)

        en_us_label = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='EN-US']/ancestor::label[contains(@class,'ms-Checkbox')]"))
                )
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", en_us_label)
        driver.execute_script("arguments[0].click();", en_us_label)
        time.sleep(1)
        print("✅ Selected EN-US option")
        time.sleep(2)
        

        save_label_span = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))
        )
        save_button = save_label_span.find_element(By.XPATH, "./ancestor::button")
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", save_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", save_button)
        print("✅ Locales saved")
        time.sleep(4)

    def _generate_and_upload_csv(self, driver):
        """Generate AI content and upload CSV"""
        print("🧠 Generating AI content...")
        
        # Generate content using GPT-4o
        input_path = os.path.join(os.path.dirname(__file__), "input.txt")
        self._generate_input_txt_via_gpt4o(input_path)
        
        # Convert to CSV
        output_path = os.path.join(os.path.dirname(__file__), "output.csv")
        self._generate_csv_from_input_file(input_path, output_path)
        
        # Upload CSV
        self._autofill_from_csv(driver, output_path)

    def _generate_input_txt_via_gpt4o(self, input_path):
        """Generate creative content using GPT-4o"""
        prompt = """You are a creative assistant helping promote the upgrade from Windows 10 to Windows 11 due to the end of support for Windows 10.

Please generate one complete creative entry in the following key-value format, one field per line. Use plain English, no quotes, no explanations.

For each ReserveString, generate a unique, helpful, or creative message related to Windows 11 upgrade, user motivation, or feature highlights.
Output exactly these fields in this order:

Locale:
Title:
MainPageTitle:
MainPageSubTitle:
MainPageSubTitle2:
LearnMoreButtonLabel:
SkipButtonLabel:
UpgradeButtonLabel:
PreviousButtonAltText:
NextButtonAltText:
ScheduleButton:
FeatureTitle0:
FeatureSubtitle0:
FeatureTitle1:
FeatureSubtitle1:
FeatureTitle2:
FeatureSubtitle2:
FeatureTitle3:
FeatureSubtitle3:
FeatureTitle4:
FeatureSubtitle4:
FeatureTitle5:
FeatureSubtitle5:
FeatureTitle6:
FeatureSubtitle6:
FeatureTitle7:
FeatureSubtitle7:
FeatureTitle8:
FeatureSubtitle8:
FeatureTitle9:
FeatureSubtitle9:
FeatureTitle10:
FeatureSubtitle10:
LearnMoreTitle:
LearnMoreSubTitle:
LearnMoreText:
LearnMoreIFrameNarratorContent:
LearnMoreBackButtonLabel:
EULATitle:
EULASubTitle:
EULADeclineButtonLabel:
EULAAcceptButtonLabel:
OutroTitle:
OutroSubTitle:
ContinueToDesktopButtonLabel:
OutroPageIFrameContent:
OutroPageIFrameNarratorContent:
OutroPageSecondaryButton:
LossAversionTitle:
LossAversionSubTitle:
LossAversionSkipButtonLabel:
LossAversionUpgradeButtonLabel:
LossAversionUpgradeLearnMoreButtonLabel:
LossAversionPageIFrameContent:
LossAversionPageIFrameNarratorContent:
SchedulePageTitle:
SchedulePageSubtitle:
SchedulePageNextButton:
SchedulePageBackButton:
ScheduleOptionLabel1:
ScheduleOptionLabel2:
ScheduleOptionText1:
ScheduleOptionText2:
DeclineOutroPageTitle:
DeclineOutroPageSubtitle:
DeclineOutroPageBackButton:
DeclineOutroPageNextButton:
DeclineOutroPageActionLink:
ReserveString1:
ReserveString2:
ReserveString3:
ReserveString4:
ReserveString5:
ReserveString6:
ReserveString7:
ReserveString8:
ReserveString9:
ReserveString10:
ReserveString11:
ReserveString12:
ReserveString13:
ReserveString14:
ReserveString15:
ReserveString16:
EULAString1:
EULAString2:
EULAString3:
"""

        try:
            print("🧠 Generating creative fields using GPT-4o...")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful creative assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
            )

            output_text = response.choices[0].message.content

            with open(input_path, 'w', encoding='utf-8') as f:
                f.write(output_text.strip())

            print(f"✅ Saved GPT-4o response to {input_path}")
        except Exception as e:
            print(f"❌ GPT-4o generation failed: {e}")
            suggestion = client.chat.completions.create(
                    messages = [
                        {"role":"user","content": f"Script failed with error: {str(e)}. Suggest retry logic or any other approach."}
                    ],
                    model="gpt-4o",
                )
            print(suggestion.choices[0].message.content)
            # Create fallback content
            self._create_fallback_content(input_path)

    def _create_fallback_content(self, input_path):
        """Create fallback content if AI generation fails"""
        fallback_content = """Locale: EN-US
Title: Windows 11 Upgrade
MainPageTitle: Ready for Windows 11?
MainPageSubTitle: Experience enhanced security and performance
MainPageSubTitle2: Your PC is eligible for the free upgrade
LearnMoreButtonLabel: Learn More
SkipButtonLabel: Skip
UpgradeButtonLabel: Upgrade Now
PreviousButtonAltText: Previous
NextButtonAltText: Next
ScheduleButton: Schedule
FeatureTitle0: Enhanced Security
FeatureSubtitle0: Built-in protection you can trust
FeatureTitle1: Improved Performance
FeatureSubtitle1: Faster boot times and responsiveness
FeatureTitle2: New Features
FeatureSubtitle2: Redesigned Start menu and taskbar
FeatureTitle3: Microsoft Teams
FeatureSubtitle3: Connect with friends and family
FeatureTitle4: Voice Typing
FeatureSubtitle4: Speak naturally to type faster
FeatureTitle5: Widgets
FeatureSubtitle5: Personalized news and information
FeatureTitle6: Virtual Desktops
FeatureSubtitle6: Organize your workspace better
FeatureTitle7: Focus Assist
FeatureSubtitle7: Stay productive with fewer distractions
FeatureTitle8: Gaming Features
FeatureSubtitle8: Enhanced gaming experience
FeatureTitle9: Accessibility
FeatureSubtitle9: Tools for everyone to use Windows
FeatureTitle10: Microsoft Store
FeatureSubtitle10: Discover new apps and entertainment
LearnMorePageTitle: Learn More About Windows 11
LearnMorePageSubtitle: Discover what's new
LearnMoreText: Windows 11 brings you closer to what you love with faster performance, enhanced security, and a beautiful new design.
LearnMorePageIFrameNarratorContent: Learn more about Windows 11 features and benefits
LearnMorePageBackButtonLabel: Back
EULAPageTitle: End of Life Support
EULAPageSubTitle: Windows 10 support ends October 2025
EULADeclineButtonLabel: Decline
EULAAcceptButtonLabel: Accept
OutroPageTitle: Welcome to Windows 11
OutroPageSubTitle: You're all set to enjoy Windows 11
ContinueToDesktopButtonLabel: Continue to Desktop
OutroPageIFrameContent: Explore Windows 11 features in this interactive guide
OutroPageIFrameNarratorContent: Windows 11 overview and feature highlights
OutroPageSecondaryButton: Explore Features
LossAversionPageTitle: Don't miss out on Windows 11
LossAversionPageSubTitle: Upgrade before support ends
LossAversionSkipButtonLabel: Skip for now
LossAversionUpgradeButtonLabel: Upgrade to Windows 11
LossAversionUpgradeLearnMoreButtonLabel: Learn about the benefits
LossAversionPageIFrameContent: Interactive Windows 11 feature demonstration
LossAversionPageIFrameNarratorContent: Discover Windows 11 capabilities and improvements
SchedulePageTitle: Choose your upgrade time
SchedulePageSubtitle: Schedule your Windows 11 upgrade
SchedulePageNextButton: Next
SchedulePageBackButton: Back
ScheduleOptionLabel1: Upgrade tonight
ScheduleOptionLabel2: Schedule for later
ScheduleOptionText1: Install during off-hours
ScheduleOptionText2: Choose a convenient time
DeclineOutroPageTitle: Continue with Windows 10
DeclineOutroPageSubtitle: You'll miss out on new features
DeclineOutroPageBackButton: Go back
DeclineOutroPageNextButton: Remind me later
DeclineOutroPageActionLink: Download Windows 11 now
ReserveString1:
ReserveString2:
ReserveString3:
ReserveString4:
ReserveString5:
ReserveString6:
ReserveString7:
ReserveString8:
ReserveString9:
ReserveString10:
ReserveString11:
ReserveString12:
ReserveString13:
ReserveString14:
ReserveString15:
ReserveString16:
EULAString1: By upgrading, you agree to the license terms
EULAString2: Windows 11 License Agreement
EULAString3: Review terms and conditions"""

        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(fallback_content)
        print(f"✅ Created fallback content at {input_path}")

    def _generate_csv_from_input_file(self, input_file, output_file):
        """Convert input file to CSV with labels and ordered keys."""
        import csv

        ordered_keys = [
            "Locale","Title","MainPageTitle","MainPageSubTitle","MainPageSubTitle2","LearnMoreButtonLabel","SkipButtonLabel","UpgradeButtonLabel",
"PreviousButtonAltText","NextButtonAltText","ScheduleButton","FeatureTitle0","FeatureSubtitle0","FeatureTitle1","FeatureSubtitle1",
"FeatureTitle2","FeatureSubtitle2","FeatureTitle3","FeatureSubtitle3","FeatureTitle4","FeatureSubtitle4","FeatureTitle5","FeatureSubtitle5",
"FeatureTitle6","FeatureSubtitle6","FeatureTitle7","FeatureSubtitle7","FeatureTitle8","FeatureSubtitle8","FeatureTitle9","FeatureSubtitle9",
"FeatureTitle10","FeatureSubtitle10","LearnMoreTitle","LearnMoreSubTitle","LearnMoreText","LearnMoreIFrameNarratorContent",
"LearnMoreBackButtonLabel","EULATitle","EULASubTitle","EULADeclineButtonLabel","EULAAcceptButtonLabel","OutroTitle",
"OutroSubTitle","ContinueToDesktopButtonLabel","OutroPageIFrameContent","OutroPageIFrameNarratorContent","OutroPageSecondaryButton",
"LossAversionTitle","LossAversionSubTitle","LossAversionSkipButtonLabel","LossAversionUpgradeButtonLabel",
"LossAversionUpgradeLearnMoreButtonLabel","LossAversionPageIFrameContent","LossAversionPageIFrameNarratorContent","SchedulePageTitle",
"SchedulePageSubtitle","SchedulePageNextButton","SchedulePageBackButton","ScheduleOptionLabel1","ScheduleOptionLabel2","ScheduleOptionText1",
"ScheduleOptionText2","DeclineOutroPageTitle","DeclineOutroPageSubtitle","DeclineOutroPageBackButton","DeclineOutroPageNextButton",
"DeclineOutroPageActionLink","ReserveString1","ReserveString2","ReserveString3","ReserveString4","ReserveString5","ReserveString6",
"ReserveString7","ReserveString8","ReserveString9","ReserveString10","ReserveString11","ReserveString12","ReserveString13","ReserveString14",
"ReserveString15","ReserveString16","EULAString1","EULAString2","EULAString3"
        ]

        human_labels = [
           "Locale","Title","Main Page Title","Main Page Subtitle","Main Page Subtitle 2","Learn More Button Label","Skip Button Label","Upgrade Button Label",
"Previous Button Alt Text","Next Button Alt Text","Schedule Button","Feature Title 0","Feature Subtitle 0","Feature Title 1","Feature Subtitle 1",
"Feature Title 2","Feature Subtitle 2","Feature Title 3","Feature Subtitle 3","Feature Title 4","Feature Subtitle 4","Feature Title 5","Feature Subtitle 5",
"Feature Title 6","Feature Subtitle 6","Feature Title 7","Feature Subtitle 7","Feature Title 8","Feature Subtitle 8","Feature Title 9","Feature Subtitle 9",
"Feature Title 10","Feature Subtitle 10","Learn More Title","Learn More SubTitle","Learn More Text","Learn More IFrame Narrator Content",
"Learn More Back Button Label","EULA Title","EULA SubTitle","EULA Decline Button Label","EULA Accept Button Label","Outro Title",
"Outro SubTitle","Continue To Desktop Button Label","Outro Page IFrame Content","Outro Page IFrame Narrator Content","Outro Page Secondary Button",
"Loss Aversion Title","Loss Aversion SubTitle","Loss Aversion Skip Button Label","Loss Aversion Upgrade Button Label",
"Loss Aversion Upgrade Learn More Button Label","Loss Aversion IFrame Content","Loss Aversion IFrame Narrator Content","Schedule Page Title",
"Schedule Page Subtitle","Schedule Page Next Button","Schedule Page Back Button","Schedule Option Label 1","Schedule Option Label 2","Schedule Option Text 1",
"Schedule Option Text 2","Decline Outro Page Title","Decline Outro Page Subtitle","Decline Outro Page Back Button","Decline Outro Page Next Button",
"Decline Outro Page Action Link","Reserve String 1","Reserve String 2","Reserve String 3","Reserve String 4","Reserve String 5","Reserve String 6",
"Reserve String 7","Reserve String 8","Reserve String 9","Reserve String 10","Reserve String 11","Reserve String 12","Reserve String 13","Reserve String 14",
"Reserve String 15","Reserve String 16","EULAString1","EULAString2","EULAString3"
        ]

        data_map = {}
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data_map[key.strip()] = value.strip()

        locale_raw = data_map.get("Locale", "").strip()
        if locale_raw.lower() == "en-us":
            data_map["Locale"] = "EN-US"
        else:
            print(f"⚠️ Locale '{locale_raw}' is not EN-US, setting to default EN-US")
            data_map["Locale"] = "EN-US"  # Ensure Locale is set to EN-US
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            writer.writerow(ordered_keys)
            writer.writerow(human_labels)
            writer.writerow([data_map.get(k, "") for k in ordered_keys])

        
        print(f"✅ CSV successfully written to {output_file}")

    def _autofill_from_csv(self, driver, csv_path):
        """Upload CSV file for autofill"""
        print("➡️ Clicking 'Auto-fill from CSV' button...")
        csv_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Auto-fill from CSV']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", csv_button)
        driver.execute_script("arguments[0].click();", csv_button)
        time.sleep(2)

        print("📂 Uploading CSV file...")
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        file_input.send_keys(csv_path)
        time.sleep(1)

        print("⬆️ Clicking final 'Upload' button...")
        upload_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Upload']"))
        )
        driver.execute_script("arguments[0].click();", upload_button)
        print("✅ CSV uploaded and autofill completed")
        
        time.sleep(3)

    def _save_draft(self, driver):
        """Save the creative as draft"""
        print("🖱️ Saving draft...")
        
        wait = WebDriverWait(driver, 10)
        save_draft_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[contains(@class,'ms-Button-label') and text()='Save draft Creative']"
        )))
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", save_draft_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", save_draft_button)
        print("✅ Clicked 'Save draft Creative'")
        time.sleep(2)

        save_final_draft_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//span[contains(@class,'ms-Button-label') and text()='Yes']"
        )))
        driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", save_final_draft_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", save_final_draft_button)
        print("✅ Final confirmation clicked")
        time.sleep(2)

    def slow_scroll_page(self, driver, step=200, delay=0.5):
        """
        Slowly scrolls the page from top to bottom for visual verification.
        """
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        while current_position < scroll_height:
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(delay)
            current_position += step
        # Ensure we reach the bottom
        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(delay)
        print("✅ Slow scroll complete for verification.")

    def fill_config_inputs(self, driver):
        settings = self.config["settings"]
        field_map = self.config.get("field_map", {})

        input_fields = {
            placeholder: settings.get(setting_key, "")
            for placeholder, setting_key in field_map.items()
        }

        for placeholder, value in input_fields.items():
            try:
                input_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//input[@placeholder='{placeholder}']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", input_elem)
                time.sleep(1)
                input_elem.clear()
                input_elem.send_keys(value)
                input_elem.send_keys(Keys.TAB)
                print(f"✅ {placeholder} populated")
            except Exception as e:
                print(f"❌ {placeholder} input not found or failed to populate: {e}")