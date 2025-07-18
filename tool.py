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

class NavigatorTool(BaseTool):
    name: str = "navigator_tool"
    description: str = "Launches Edge and logs into IRIS Studio to create campaigns"

    def _run(self, input: str = "") -> str:  # FIXED: Added default value
        print(">>> NavigatorTool _run called!")
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

            # Handle checkbox
            # try:
            #     checkbox_label = driver.find_element(By.XPATH, "//label[@for='checkbox-71']")
            #     checkbox_label.click()
            #     print("✅ Notice checkbox ticked.")
            # except Exception:
            #     try:
            #         checkbox = driver.find_element(By.ID, "checkbox-71")
            #         driver.execute_script("arguments[0].click();", checkbox)
            #         print("✅ Notice checkbox ticked using script.")
            #     except Exception as e:
            #         print(f"⚠ Could not find or click the notice checkbox: {e}")

            # # Click Proceed
            # try:
            #     proceed_button = driver.find_element(By.XPATH, "//button[contains(., 'Proceed')]")
            #     proceed_button.click()
            #     print("✅ 'Proceed' button clicked.")
            #     time.sleep(3)
            # except Exception as e:
            #     suggestion = client.chat.completions.create(
            #         messages = [
            #             {"role":"user","content": f"Selenium failed with error: {str(e)}. Suggest retry logic or alt XPath."}
            #         ],
            #         model="gpt-4o",
            #     )
            #     print("🤖 AI Suggestion:")
            #     print(suggestion.choices[0].message.content)

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
                campaign_name_input.send_keys("try 63 Upgrade Campaign - AI Generated")
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

                    target_date = "4, July, 2025"
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

if __name__ == "__main__":
    tool = NavigatorTool()
    result = tool._run()
    print(result)
