# TODO: utilz go here 

import requests as r

# TODO: 
# [] Cleanup to stock.db and smooth etl upsertion via actions
# [] EDA/LSTM app templating on panel
# [] Changes to utils 
# [] rebuild docker and deploy



# discord webhook 


urls = "https://discord.com/api/webhooks/1298490100736458844/AdBPy6LBJyrrZ6tTkA2sZMsdgZXEbrWudgi6QuTtd7wTJ6plscpWtVBGSqCaFXX8lVFT"
payload = {"content": "test"}

response = r.post(urls, json=payload)


def discord_logger(webhook_url, message):
    payload={"content": message}
    response = r.post(webhook_url, json=payload)
    
    return response

discord_logger(urls, "It works haha haha")


# ------ /// SQLite3 func.




# ------- /// env load



# ------/// others 