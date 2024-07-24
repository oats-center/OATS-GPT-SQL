# Preview 
This code will allow you to create a local api for your sql database.  We will then connect the API to chatGPT using NGROK, allowing it to interact with the database

# STEPS 
1: connect to tailscale (make sure account has access to ai_playground database or whatever database for usage) \
2: clone the repository \
3: install requirements.txt in your environment \
4: (In the gpt_sql.py file) enter table_catalog variable with the database_name \
5: (In the gpt_sql.py file) create a connection link with the given format \
6: run "python {file_name}.py" in terminal to start the local host \
7: In the output, you will see a link after "running on", it will look like this "Running on 'Link'". That link will be used for the NGROK <LOCALHOST_HTTP_LINK_HERE>


# Using NGROK to Connect Local Host to Internet (https://ngrok.com/download)
**BEFORE INSTALLATION** \
1: run command prompt with administrator access  
2: run "choco install ngrok" for Windows and "brew install ngrok/ngrok/ngrok" on Mac \
3: run "ngrok config add-authtoken <AUTHCODE_HERE>" (authcode will be given when making ngrok account)

**AFTER INSTALLTION** \
1: ngrok http <LOCALHOST_HTTP_LINK_HERE> \
2: "Forwarding" link will be the link used for the external api endpoint \
3: (optional) run pyhoncode below to test 
```
import requests

base_url = #TODO REPLACE WITH GIVEN FORWARDING LINK

table_name = #REPLACE WITH TABLE NAME
column_name = #REPLACE WITH COLUMN NAME (MUST BE VALUE SINCE WE'RE TESTING AVERAGE"

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
# Replace with the correct link in chat GPT
1: Open chat-GPT \
2: On the custom gpts, find the "Weather+DB GPT"  \
3: Go to edit GPT on the top left \
4: scroll down and edit the ngrok action (Not the api.weather one) \
5: Replace the find the "servers" section under the schema (should be near the top) and replace the url with the "forwarding" Link given by NGROK \
6: (MAKE SURE NOT TO CLOESE NGROK, THIS LINK WILL HAVE TO BE REPLACED EVERY TIME YOU CLOSE THE LOCAL HOST/NGROK) \
7: Update the custom GPT and test!

