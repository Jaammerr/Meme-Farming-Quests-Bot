
# Stakeland Farm Bot

## 🔗 Links

🔔 CHANNEL: https://t.me/JamBitPY

💬 CHAT: https://t.me/JamBitChat

💰 DONATION EVM ADDRESS: 0xe23380ae575D990BebB3b81DB2F90Ce7eDbB6dDa


## 🤖 | Features:

- **Auto registration**
- **Auto bind twitter**
- **Auto completing all possible quests**

## 🚀 Installation


`` Required python >= 3.10``

``1. Close the repo and open CMD (console) inside it``

``2. Install requirements: pip install -r requirements.txt``

``3. Setup configuration and accounts``

``4. Run: python run.py``


## ⚙️ Config (config > settings.yaml)

| Name | Description                                                                                        |
| --- |----------------------------------------------------------------------------------------------------|
| eth_rpc | ETH RPC URL (if not have, leave the default value)                                                 |
| threads | Number of accounts that will work in parallel |
| delay_between_quests | delay between quests |


## ⚙️ Accounts format (config > accounts.txt)

- twitter_auth_token|wallet_mnemonic/private_key|proxy

`` Proxy format: IP:PORT:USER:PASS``


## 📄 Results
```After the script is finished, the results will be saved in the config folder in files success_accounts.txt/failed_accounts.txt```
