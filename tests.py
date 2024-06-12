import unittest
import time
import requests
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
product_api_url = 'http://localhost:3000/product'

class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=UiAutomator2Options().load_capabilities(capabilities))

        # Create client
        client_data = {
            "name": "Pepe3",
            "lastName": "Carlos3",
            "email": "carlos10.doe@example.com",
            "address": "123456 Main St"
        }
        client_response = requests.post(client_api_url, json=client_data)
        print(f"Client creation response: {client_response.json()}")
        self.client_id = int(client_response.json().get('id'))

        # Create provider
        provider_data = {
            "name": "ProviderName3",
            "lastName": "ProviderLastname3",
            "email": "provider10@example.com"
        }
        provider_response = requests.post(provider_api_url, json=provider_data)
        print(f"Provider creation response: {provider_response.json()}")
        self.provider_id = int(provider_response.json().get('id'))

        # Create warehouse
        warehouse_data = {
            "address": "Warehouse Address 4",
            "providerId": self.provider_id
        }
        warehouse_response = requests.post(warehouse_api_url, json=warehouse_data)
        print(f"Warehouse creation response: {warehouse_response.json()}")
        self.warehouse_id = int(warehouse_response.json().get('id'))

        product_data= {
            "name": 'example product10 '
        }

        product_response = requests.post(product_api_url, json=product_data)
        print(f"Product creation response: {product_response.json()}")
        self.product_id = int(product_response.json().get('id'))
        associate_product_response = requests.post(f'{warehouse_api_url}/{self.warehouse_id}', json={
            "productId": self.product_id,
            "stock": 20
        })

        print(f"Product/warehouse association response content: {associate_product_response.text}")
        print(f"Product/warehouse association response status code: {associate_product_response.status_code}")

        associate_provider_product_response = requests.post(f'{provider_api_url}/{self.provider_id}', json={
            "productId": self.product_id,
            "price": 100
        })

        print(f"Product/provider association response content: {associate_provider_product_response.text}")

        # Create order
        order_data = {
            "clientId": self.client_id,
            "providerId": self.provider_id,
            "products": [
                {
                    "productId": self.product_id,
                    "quantity": 1
                }
            ]
        }
        self.order_response = requests.post(order_api_url, json=order_data)
        print(f"Order creation response: {self.order_response.json()}")

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_input_clientID(self) -> None:
        # Wait for the element to be visible and input the client ID
        wait = WebDriverWait(self.driver, 20)
        el = wait.until(EC.visibility_of_element_located((AppiumBy.XPATH, '//*[@text="Enter Client ID"]')))
        el.send_keys(str(self.client_id))

        # Add a short wait to allow input processing
        time.sleep(2)

        # Verify if the text "Status: ACCEPTED" is present
        self.get_order_status()

    def get_order_status(self) -> None:
        # Wait for the ViewGroup element
        wait = WebDriverWait(self.driver, 10)
        view_group_element = wait.until(EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR,
                                                                        'new UiSelector().className("android.view.ViewGroup").instance(9)')))

        # Add a short wait to ensure all elements inside the ViewGroup are loaded
        time.sleep(2)

        # Check if the text "ACCEPTED" is present inside the ViewGroup
        accepted_status_elements = view_group_element.find_elements(by=AppiumBy.ANDROID_UIAUTOMATOR,
                                                                    value='new UiSelector().textContains("PENDING")')

        if accepted_status_elements:
            print("The text 'PENDING' is present inside the ViewGroup.")
            status_present = True
        else:
            print("The text 'PENDING' is not present inside the ViewGroup.")
            status_present = False

        # Assert that the status is present
        self.assertTrue(status_present, "The text 'PENDING' should be present inside the ViewGroup.")

if __name__ == '__main__':
    unittest.main()
