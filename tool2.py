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
        with open(os.path.join(os.path.dirname(__file__), "config.json"), 'r') as f:
            object.__setattr__(self, 'config', json.load(f))

    def _get_image_path(self, label_name):
        """Get full image path from config"""
        base_dir = self.config["image_paths"]["base_directory"]
        filename = self.config["image_paths"]["images"].get(label_name)
        if not filename:
            print(f"⚠️ Image not found in config for label: {label_name}")
            return None
        return os.path.join(base_dir, filename)

    def _run(self, input: str = "") -> str:
        print(">>> NavigatorTool _run called!")
        driver = None
        # self._generate_and_upload_csv(driver)

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
                

                # Fill Creative Name
                wait = WebDriverWait(driver, 10)
                name_input = wait.until(EC.presence_of_element_located((
                    By.XPATH, "//input[contains(@placeholder,'Enter a name for your Creative')]"
                )))
                name_input.send_keys(self.config["settings"]["creative_name"])
                time.sleep(1)

                if name_input.get_attribute('value') != self.config["settings"]["creative_name"]:
                    driver.execute_script("arguments[0].value = arguments[1];", name_input, self.config["settings"]["creative_name"])

                print("✅ Entered creative name.")
                time.sleep(1)



                try:
                    time.sleep(2)
                    surface_dropdown = WebDriverWait(driver, 10).until(
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



                # Navigate to Creative Editor
                try:
                    time.sleep(2)
                    # Find the Generate Creative button by its label text
                    generate_button = WebDriverWait(driver, 10).until(
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
                driver.get(
                   "https://portal.cpm.microsoft.com/creatives/14223966315993355067_128000000005505669"
                )
                
                try:
                    time.sleep(5)

                    # self.fill_config_inputs(driver)
                except Exception as e:
                    print(f"⚠️ Error filling config inputs: {e}")
                
                
                # try:
                #     time.sleep(3)
                #     ndup_input = WebDriverWait(driver, 15).until(
                #         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='NDUP ID']"))
                #     )
                #     driver.execute_script("arguments[0].scrollIntoView(true);", ndup_input)
                #     time.sleep(1)
                #     ndup_input.clear()
                #     ndup_input.send_keys(self.config["settings"]["ndup_id"])
                #     ndup_input.send_keys(Keys.TAB)
                #     print("✅ NDUP ID populated")
                # except Exception as e:
                #     print(f"❌ NDUP ID input not found or failed to populate: {e}")

                # try:
                #     time.sleep(3)
                #     ndup_input = WebDriverWait(driver, 15).until(
                #         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='NDUP ID']"))
                #     )
                #     driver.execute_script("arguments[0].scrollIntoView(true);", ndup_input)
                #     time.sleep(1)
                #     ndup_input.clear()
                #     ndup_input.send_keys(self.config["settings"]["ndup_id"])
                #     ndup_input.send_keys(Keys.TAB)
                #     print("✅ NDUP ID populated")
                # except Exception as e:
                #     print(f"❌ NDUP ID input not found or failed to populate: {e}")

                # try:
                #     time.sleep(3)
                #     ndup_input = WebDriverWait(driver, 15).until(
                #         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Tips Timeout']"))
                #     )
                #     driver.execute_script("arguments[0].scrollIntoView(true);", ndup_input)
                #     time.sleep(1)
                #     ndup_input.clear()
                #     ndup_input.send_keys(self.config["settings"]["tips_timeout"])
                #     ndup_input.send_keys(Keys.TAB)
                #     print("✅ Tips Timeout populated")
                # except Exception as e:
                #     print(f"❌ Tips Timeout input not found or failed to populate: {e}")



                # try:
                #     time.sleep(3)
                #     ndup_input = WebDriverWait(driver, 15).until(
                #         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Tips Count']"))
                #     )
                #     driver.execute_script("arguments[0].scrollIntoView(true);", ndup_input)
                #     time.sleep(1)
                #     ndup_input.clear()
                #     ndup_input.send_keys(self.config["settings"]["tips_count"])
                #     ndup_input.send_keys(Keys.TAB)
                #     print("✅ Tips Count populated")
                # except Exception as e:
                #     print(f"❌ Tips Count input not found or failed to populate: {e}")



                # try:
                #     time.sleep(3)
                #     ndup_input = WebDriverWait(driver, 15).until(
                #         EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Type']"))
                #     )
                #     driver.execute_script("arguments[0].scrollIntoView(true);", ndup_input)
                #     time.sleep(1)
                #     ndup_input.clear()
                #     ndup_input.send_keys(self.config["settings"]["type"])
                #     ndup_input.send_keys(Keys.TAB)
                #     print("✅ Type populated")
                # except Exception as e:
                #     print(f"❌ Type input not found or failed to populate: {e}")








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



                


                # print("📸 Starting image uploads from configuration...")
                # for label_name in self.config["image_paths"]["images"]:
                #     image_path = self._get_image_path(label_name)
                #     if image_path:
                #         self._upload_image(driver, image_path, label_name)
                #     else:
                #         print(f"⚠️ Skipping {label_name} - image path not found")

                # choose_locales_btn = driver.find_element(By.XPATH, "//span[contains(text(),'Choose Locales')]")
                # driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", choose_locales_btn)
                # time.sleep(1)
                # driver.execute_script("arguments[0].click();", choose_locales_btn)
                # print("✅ Choose Locales button clicked")
                # time.sleep(2)

                # filter_input = WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Filter by name']"))
                # )
                # filter_input.clear()
                # filter_input.send_keys("EN-US")
                # print("✅ Typed EN-US in filter box")
                # time.sleep(2)

                # en_us_label = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, "//span[text()='EN-US']/ancestor::label[contains(@class,'ms-Checkbox')]"))
                # )
                # driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", en_us_label)
                # driver.execute_script("arguments[0].click();", en_us_label)
                # time.sleep(1)
                # print("✅ Selected EN-US option")
                # time.sleep(2)

                # save_label_span = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))
                # )
                # save_button = save_label_span.find_element(By.XPATH, "./ancestor::button")
                # driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth',block:'center'});", save_button)
                # time.sleep(1)
                # driver.execute_script("arguments[0].click();", save_button)
                # print("✅ Locales saved")
                # time.sleep(4)



            except Exception as e:
                print(f"❌ Error during creative workflow: {e}")
                return f"❌ Error during creative workflow: {e}"

        except Exception as e:
            print(f"❌ Error in NavigatorTool: {e}")
            return f"❌ Error in NavigatorTool: {e}"
                
        # try:
        #     self.slow_scroll_page(driver, step=200, delay=0.5)
        finally:
            if driver:
                driver.quit()
   
    def _upload_image(self, driver, image_path, label_name):
        """Upload image to specified label field"""
        print(f"📸 Uploading image to '{label_name}'...")

        if not os.path.exists(image_path):
            print(f"❌ Image file not found: {image_path}")
            return False

        try:
            wait = WebDriverWait(driver, 10)

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
                driver.execute_script(
                "arguments[0].style.border='3px solid orange'; arguments[0].style.background='#fff8dc';", input_elem
            )
                driver.execute_script("arguments[0].scrollIntoView(true);", input_elem)
                time.sleep(1)
                input_elem.clear()
                input_elem.send_keys(value)
                input_elem.send_keys(Keys.TAB)
                print(f"✅ {placeholder} populated with '{value}'")
            except Exception as e:
                print(f"❌ Failed to populate '{placeholder}': {e}")       

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
    def _generate_input_txt_via_gpt4o(self, input_path):
        """Generate creative content using GPT-4o"""
        prompt = """You are a creative assistant helping promote the upgrade from Windows 10 to Windows 11 due to the end of support for Windows 10.

Please generate one complete creative entry in the following key-value format, one field per line. Use plain English, no quotes, no explanations.

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
        # self._autofill_from_csv(driver, output_path)
if __name__ == "__main__":
    tool = NavigatorTool()
    result = tool._run()
    print(result)