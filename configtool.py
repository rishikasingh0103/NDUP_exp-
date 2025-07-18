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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open(os.path.join(os.path.dirname(__file__), "tryconfig.json"), 'r') as f:
            object.__setattr__(self, 'tryconfig', json.load(f))


    def _run(self, input: str = "") -> str:
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

            # --- Example: Click Creatives, New Creative, fill name, etc. ---
            try:
                
                checkbox_box = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='I have read and acknowledge this message.']/preceding::div[contains(@class,'ms-Checkbox-checkbox')][1]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox_box)
                driver.execute_script("arguments[0].click();", checkbox_box)
                print("✅ Checkbox ticked using label-based path.")
            except Exception as e:
                print(f"❌ Failed to tick checkbox: {e}")
            
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

           


                driver.get(
                   "https://portal.cpm.microsoft.com/creatives/14223966315993355067_128000000005505669"
                )
                try:
                    time.sleep(5)
                    self.fill_config_inputs(driver)
                except Exception as e:
                    print(f"⚠️ Error filling config inputs: {e}")
                
               






                time.sleep(5)
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



                


              



            except Exception as e:
                print(f"❌ Error during creative workflow: {e}")
                return f"❌ Error during creative workflow: {e}"

        except Exception as e:
            print(f"❌ Error in NavigatorTool: {e}")
            return f"❌ Error in NavigatorTool: {e}"
                
        try:
            self.slow_scroll_page(driver, step=200, delay=0.5)
        finally:
            if driver:
                driver.quit()
   

    def fill_config_inputs(self, driver):
        """
        Auto-fills all fields specified in config['field_map'] by matching placeholder text.
        """
        print("🔍 Dynamically filling inputs from config['field_map']...")
        field_map = self.config.get("field_map", {})
        for placeholder, value in field_map.items():
            try:
                time.sleep(2)
                input_elem = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, f"//input[@placeholder='{placeholder}']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", input_elem)
                time.sleep(1)
                input_elem.clear()
                input_elem.send_keys(value)
                input_elem.send_keys(Keys.TAB)
                print(f"✅ {placeholder} populated with '{value}'")
            except Exception as e:
                print(f"❌ Failed to populate '{placeholder}': {e}")       

    

    
        

if __name__ == "__main__":
    tool = NavigatorTool()
    result = tool._run()
    print(result)