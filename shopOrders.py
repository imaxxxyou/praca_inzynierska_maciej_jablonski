import requests
import json
from woocommerce import api

class WooCommerceAPI:
    def __init__(self, consumer_key, consumer_secret, base_url):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = base_url

    def get_customers(self):
        endpoint = "/wp-json/wc/v3/customers"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))

        if response.status_code == 200:
            orders = response.json()
            return orders
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_orders(self):
        endpoint = "/wp-json/wc/v3/orders"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))

        if response.status_code == 200:
            orders = response.json()
            return orders
        else:
            print(f"Error: {response.status_code}")
            return None

    def get_products(self):
        endpoint = "/wp-json/wc/v3/products"
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))

        if response.status_code == 200:
            orders = response.json()
            return orders
        else:
            print(f"Error: {response.status_code}")
            return None


if __name__ == "__main__":
    # Ustawienia
    consumer_key = "ck_d449de73f3eb7dd3fb3991469032a04e408920b5"
    consumer_secret = "cs_e29ed4cee4c358981b5a4998ba6dc95cff175e54"
    base_url = "https://zwolnejreki.com.pl"  # Zmień na swój adres sklepu

    # Inicjalizacja obiektu WooCommerceAPI
    api = WooCommerceAPI(consumer_key, consumer_secret, base_url)

    # Pobierz zamówienia
    orders = api.get_orders()
    products = api.get_products()
    customers = api.get_customers()

    # Wyświetl zamówienia w formacie JSON w konsoli
    if orders:
        print(json.dumps(orders, indent=2))
    #
    # if customers:
    #     print(json.dumps(customers, indent=2))