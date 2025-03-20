import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (if available)
load_dotenv()

def get_rate(api_url):
    """
    Fetch the API response, print it for debugging,
    and compute the rate as (usd_price of GAS) / (usd_price of NEO).
    This represents the price of GAS in NEO terms.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Debug: print raw API response
        print("Raw API response:")
        print(data)
        
        neo_price = None
        gas_price = None
        
        # Loop over each item and extract prices for NEO and GAS.
        for item in data:
            if item.get("symbol") == "NEO":
                neo_price = item.get("usd_price")
            elif item.get("symbol") == "GAS":
                gas_price = item.get("usd_price")
        
        if neo_price is None:
            print("NEO price not found in the API response.")
            return None
        if gas_price is None:
            print("GAS price not found in the API response.")
            return None
        
        # Compute the rate as the price of GAS in terms of NEO.
        rate = gas_price / neo_price
        return float(rate)
    
    except Exception as e:
        print("Error fetching market rate:", e)
        return None

if __name__ == '__main__':
    # Use the API URL from the environment variable or a default value.
    api_url = os.getenv("FLAMINGO_API_URL", "https://flamingo-us-1.b-cdn.net/flamingo/live-data/prices/latest")
    print("Using API URL:", api_url)
    
    rate = get_rate(api_url)
    if rate is not None:
        print("Extracted rate (GAS/NEO):", rate)
    else:
        print("Failed to extract rate.")
