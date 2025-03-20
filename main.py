import os
import time
import logging
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FlamingoSwapBot:
    def __init__(self):
        """
        Initialize the bot with paper-trade funds and no active trades.
        Each trading channel (NEO→GAS and GAS→NEO) works independently.
        """
        # Set initial funds (adjusted for fixed orders)
        self.initial_neo = 10000.0
        self.initial_gas = 100000.0

        # Current balances
        self.neo_balance = self.initial_neo
        self.gas_balance = self.initial_gas

        # Active trade state for each channel:
        # Only one active NEO→GAS trade and one active GAS→NEO trade at any time.
        self.active_trade_neo_to_gas = None
        self.active_trade_gas_to_neo = None

        # API configuration for Flamingo live price data.
        self.api_url = os.getenv("FLAMINGO_API_URL", "https://flamingo-us-1.b-cdn.net/flamingo/live-data/prices/latest")
        
        # NEO RPC endpoint(s) (if needed later)
        neo_rpc_url = os.getenv("NEO_RPC_URL")
        if neo_rpc_url:
            self.rpc_urls = [neo_rpc_url]
        else:
            self.rpc_urls = [
                "https://mainnet1.neo.coz.io:443",
                "https://mainnet2.neo.coz.io:443",
                "https://mainnet3.neo.coz.io:443",
                "https://mainnet4.neo.coz.io:443"
            ]

        # Configure logging.
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("FlamingoSwapBot")

        # Define an entry tolerance (for example, when rate is near 0.3).
        self.entry_lower_bound = 0.2995
        self.entry_upper_bound = 0.3005

    def get_rate(self):
        """
        Fetch the API response and compute the conversion rate as the price of GAS in terms of NEO.
        (Calculated as: rate = (GAS usd_price) / (NEO usd_price))
        """
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            
            # Debug: print raw API response.
            print("Raw API response:")
            print(data)
            
            neo_price = None
            gas_price = None
            
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
            
            rate = gas_price / neo_price
            return float(rate)
        except Exception as e:
            print("Error fetching market rate:", e)
            return None

    # --- Entry conditions for each channel ---
    def check_entry_neo_to_gas(self, rate):
        """
        Check if conditions are met to enter a new NEO→GAS trade.
        A trade is entered if no NEO→GAS trade is active and the current rate is within the entry bounds.
        """
        if self.active_trade_neo_to_gas is not None:
            return False
        return self.entry_lower_bound <= rate <= self.entry_upper_bound

    def check_entry_gas_to_neo(self, rate):
        """
        Check if conditions are met to enter a new GAS→NEO trade.
        A trade is entered if no GAS→NEO trade is active and the current rate is within the entry bounds.
        """
        if self.active_trade_gas_to_neo is not None:
            return False
        return self.entry_lower_bound <= rate <= self.entry_upper_bound

    # --- NEO → GAS trade functions ---
    def enter_neo_to_gas_trade(self, rate):
        """
        Enter a NEO→GAS trade:
          - Deduct 3000 NEO and convert to GAS (gas_received = 3000 / rate).
        """
        if self.neo_balance < 3000:
            self.logger.info("Insufficient NEO to enter NEO→GAS trade.")
            return
        self.neo_balance -= 3000
        gas_received = 3000 / rate
        self.gas_balance += gas_received
        self.active_trade_neo_to_gas = {"entry_rate": rate, "gas_amount": gas_received}
        self.logger.info(
            f"Entered NEO→GAS trade at rate {rate:.4f}: -3000 NEO, +{gas_received:.2f} GAS. "
            f"Balances: {self.neo_balance:.2f} NEO, {self.gas_balance:.2f} GAS."
        )

    def check_exit_neo_to_gas(self, rate):
        """
        Exit an active NEO→GAS trade when the current rate is at least 0.001 higher than the entry rate.
        Convert all the acquired GAS back to NEO.
        """
        trade = self.active_trade_neo_to_gas
        if trade is None:
            return
        entry_rate = trade["entry_rate"]
        if rate >= entry_rate + 0.001:
            gas_amount = trade["gas_amount"]
            neo_received = gas_amount * rate
            self.gas_balance -= gas_amount
            self.neo_balance += neo_received
            self.logger.info(
                f"Exited NEO→GAS trade at rate {rate:.4f} (entry was {entry_rate:.4f}): "
                f"converted {gas_amount:.2f} GAS for {neo_received:.2f} NEO. "
                f"Balances: {self.neo_balance:.2f} NEO, {self.gas_balance:.2f} GAS."
            )
            self.active_trade_neo_to_gas = None

    # --- GAS → NEO trade functions ---
    def enter_gas_to_neo_trade(self, rate):
        """
        Enter a GAS→NEO trade:
          - Deduct 10000 GAS and convert to NEO (neo_received = 10000 * rate).
        """
        if self.gas_balance < 10000:
            self.logger.info("Insufficient GAS to enter GAS→NEO trade.")
            return
        self.gas_balance -= 10000
        neo_received = 10000 * rate
        self.neo_balance += neo_received
        self.active_trade_gas_to_neo = {"entry_rate": rate, "neo_amount": neo_received}
        self.logger.info(
            f"Entered GAS→NEO trade at rate {rate:.4f}: -10000 GAS, +{neo_received:.2f} NEO. "
            f"Balances: {self.neo_balance:.2f} NEO, {self.gas_balance:.2f} GAS."
        )

    def check_exit_gas_to_neo(self, rate):
        """
        Exit an active GAS→NEO trade when the current rate is at least 0.001 lower than the entry rate.
        Convert all the acquired NEO back to GAS.
        """
        trade = self.active_trade_gas_to_neo
        if trade is None:
            return
        entry_rate = trade["entry_rate"]
        if rate <= entry_rate - 0.001:
            neo_amount = trade["neo_amount"]
            gas_received = neo_amount / rate
            self.neo_balance -= neo_amount
            self.gas_balance += gas_received
            self.logger.info(
                f"Exited GAS→NEO trade at rate {rate:.4f} (entry was {entry_rate:.4f}): "
                f"converted {neo_amount:.2f} NEO for {gas_received:.2f} GAS. "
                f"Balances: {self.neo_balance:.2f} NEO, {self.gas_balance:.2f} GAS."
            )
            self.active_trade_gas_to_neo = None

    def run(self):
        self.logger.info("Starting Flamingo Swap Bot (independent channels)...")
        while True:
            rate = self.get_rate()
            if rate is None:
                self.logger.info("Rate unavailable. Retrying in 10 seconds...")
                time.sleep(10)
                continue

            self.logger.info(f"Current market rate (GAS/NEO): {rate:.4f}")

            # For each channel, only enter a new trade if no trade is active.
            if self.active_trade_neo_to_gas is None:
                if self.check_entry_neo_to_gas(rate):
                    self.enter_neo_to_gas_trade(rate)

            if self.active_trade_gas_to_neo is None:
                if self.check_entry_gas_to_neo(rate):
                    self.enter_gas_to_neo_trade(rate)

            # Check exit conditions for each active trade.
            self.check_exit_neo_to_gas(rate)
            self.check_exit_gas_to_neo(rate)

            self.logger.info(f"Balances: {self.neo_balance:.2f} NEO, {self.gas_balance:.2f} GAS")
            time.sleep(10)

if __name__ == '__main__':
    bot = FlamingoSwapBot()
    bot.run()
