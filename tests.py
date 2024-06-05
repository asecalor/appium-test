import unittest
import requests
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
client_api_url = 'http://localhost:3000/client'
provider_api_url = 'http://localhost:3000/provider'
warehouse_api_url = 'http://localhost:3001/warehouse'
order_api_url = 'http://localhost:3000/order'

class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))

        # Create client
        client_data = {
            "name": "John",
            "lastname": "Doe",
            "email": "john.doe@example.com",
            "address": "123 Main St"
        }
        client_response = requests.post(client_api_url, json=client_data)
        self.client_id = client_response.json().get('id')

        # Create provider
        provider_data = {
            "name": "ProviderName",
            "lastname": "ProviderLastname",
            "email": "provider@example.com"
        }
        provider_response = requests.post(provider_api_url, json=provider_data)
        self.provider_id = provider_response.json().get('id')

        # Create warehouse
        warehouse_data = {
            "address": "Warehouse Address",
            "providerId": self.provider_id
        }
        warehouse_response = requests.post(warehouse_api_url, json=warehouse_data)
        self.warehouse_id = warehouse_response.json().get('id')

        # Associate product to warehouse
        product_id = 1  # Assuming the product ID is 1 for simplicity
        requests.post(f'{warehouse_api_url}/{self.warehouse_id}', json= {
            "productId": 1,
            "stock": 20
        })
        # Create order
        order_data = {
            "clientId": self.client_id,
            "providerId": self.provider_id,
            "products": [
                {
                    "productId": product_id,
                    "quantity": 1
                }
            ]
        }
        self.order_response = requests.post(order_api_url, json=order_data)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_input_clientID(self) -> None:
        # Find the element and input the client ID
        el = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Enter Client ID"]')
        el.send_keys(str(self.client_id))

        # Verify if the text "Status: ACCEPTED" is present
        self.get_order_status()

    def get_order_status(self) -> None:
        # Find the ViewGroup element
        view_group_element = self.driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR,
                                                      value='new UiSelector().className("android.view.ViewGroup").instance(9)')
        # Check if the text "ACCEPTED" is present inside the ViewGroup
        accepted_status_elements = view_group_element.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR,
                                                                    value='new UiSelector().textContains("ACCEPTED")')

        if accepted_status_elements:
            print("The text 'ACCEPTED' is present inside the ViewGroup.")
            status_present = True
        else:
            print("The text 'ACCEPTED' is not present inside the ViewGroup.")
            status_present = False

        # Assert that the status is present
        self.assertTrue(status_present, "The text 'ACCEPTED' should be present inside the ViewGroup.")

if __name__ == '__main__':
    unittest.main()
