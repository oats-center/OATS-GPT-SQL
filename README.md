# Preview \
This code will allow you to create a local api for your sql database. Which we will then connect to chatGPT using NGROK which will allow it to interact with the database

# STEPS \
1: connect to 


# USING NGROK
**BEFORE INSTALLATION** \
1: run command prompt in terminal  
2: choco install ngrok \
3: ngrok config add-authtoken <AUTHCODE_HERE> 

**AFTER INSTALLTION** \
4: ngrok http <LOCALHOST_HTTP_LINK_HERE> \
5: "Forwarding" link will be the link used for the external api endpoint \
6: use Link above for the custum GPT \
7: (optional) run code below to test 
```
import requests

base_url = 'https://62c4-52-119-103-50.ngrok-free.app'

table_name = 'newa_weather'
column_name = 'prcp'

url = f'{base_url}/get_avg/{table_name}/{column_name}'

response = requests.get(url)

if response.status_code == 200:
    try:
        data = response.json()
        print(data)
    except requests.exceptions.JSONDecodeError:
        print("Not JSON Format Error")
else:
    print(f"Error Code: {response.status_code}")
    print(f"Response Content: {response.content}")
```

