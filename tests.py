import unittest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

capabilities = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='emulator-5554',
    appPackage='com.valendc15.myapp',
    appActivity='.MainActivity',
    language='en',
    locale='US',
)

appium_server_url = 'http://localhost:4723'


class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_input_clientID(self) -> None:
        # Find my-app

        # app=self.driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value='my-app on Valentinos-MacBook-Air.local, exp://192.168.1.13:8081')
        # app.click()

        # Find the element and input "1"
        el = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Enter Client ID"]')
        el.send_keys("1")

        # Verify if the text "Status: ACCEPTED" is present
        self.get_order_status()

    def get_order_status(self) -> None:
        # Check if the text "Status: ACCEPTED" is present
        accepted_status_elements = self.driver.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR,
                                                             value='new UiSelector().text("Status: ACCEPTED")'
                                                             )

        if accepted_status_elements:
            print("The text 'Status: ACCEPTED' is present on the screen.")
            status_present = True
        else:
            print("The text 'Status: ACCEPTED' is not present on the screen.")
            status_present = False

        # Assert that the status is present
        self.assertTrue(status_present, "The text 'Status: ACCEPTED' should be present on the screen.")

if __name__ == '__main__':
    unittest.main()

