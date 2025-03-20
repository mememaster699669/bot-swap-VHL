# FlamingoSwapBot - Automated Trading Bot for NEO/GAS Arbitrage

## 📌 Description
FlamingoSwapBot is a personal project designed to automate trading between NEO and GAS on the Flamingo Finance ecosystem. The bot operates two independent trading strategies:
- **NEO → GAS arbitrage**
- **GAS → NEO arbitrage**

The objective is to accumulate more crypto assets by taking advantage of small fluctuations in exchange rates, without caring about their value in USD.

## ⚙️ Features
- Real-time market data via Flamingo API
- Two independent trading channels (NEO→GAS and GAS→NEO)
- Entry/exit strategies based on predefined price tolerance thresholds
- Simulated balances and paper-trading logic
- Custom logging system for monitoring performance and trades
- Configurable via `.env` file

## 🧠 Strategy
The bot:
- Monitors the current exchange rate between NEO and GAS
- Enters trades when the rate is favorable (within a defined tolerance range)
- Exits trades once a profit threshold is met
- Ensures only one active trade per channel to manage risk
- Focuses on increasing asset quantity, not USD value

## 📂 Structure
. ├── main.py # Core logic and execution loop 
  ├── .env # Contains API and RPC URLs (not included in repo) 
  ├── README.txt # Project documentation 


## 🔧 Configuration (.env file)
Create a .env file in the root directory with the following keys:
FLAMINGO_API_URL=https://flamingo-us-1.b-cdn.net/flamingo/live-data/prices/latest NEO_RPC_URL=https://mainnet1.neo.coz.io:443


## 🚀 How to Run
```bash
pip install -r requirements.txt
python main.py
📈 Example Trade Flow
Enters a NEO→GAS trade at a low rate.
Waits for a favorable rate increase.
Converts GAS back to NEO for profit.
Repeats the cycle independently for GAS→NEO direction.
💡 Notes
This is a paper trading (simulation) bot. No real funds are used or transferred.
The strategy is asset-quantity based, not fiat-value based.
For real deployment, more security and error handling would be necessary.
👨‍💻 Author
Created by Long, as part of a personal project to experiment with trading automation and algorithmic strategies.

