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
2: run "choco install ngrok" for Windows or "brew install ngrok/ngrok/ngrok" on Mac \
3: run "ngrok config add-authtoken <AUTHCODE_HERE>" (authcode will be given when making ngrok account)

**AFTER INSTALLTION** \
1: ngrok http <LOCALHOST_HTTP_LINK_HERE> \
2: "Forwarding" link will be the link used for the external api endpoint \
3: (optional) run python code below to test 
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


```
import requests
import json
import datetime
from datetime import date
from datetime import timedelta
import psycopg2

def run_query(input_query):
    # Connect to oats1.server.oats server
    # Requires tailscale to be active
    CONNECTION = "postgresql://lool:XDW!qNNJ-47K!Rm@oats1.server.oats:5432/ai_playground"

    conn = None

    try:
        print("Connecting to purdue database...")

        # Create a connection with the database
        conn = psycopg2.connect(CONNECTION)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        # Run the input query on the database
        # Must be in the format of an SQL query string ending in a ';'
        cursor.execute(input_query)

        info = None

        if input_query.strip().lower().startswith("select"):
            info = cursor.fetchall()  # Fetch all rows for SELECT queries
        else:
            conn.commit()  # Commit changes for non-SELECT queries

        # Close the cursor
        cursor.close()

        # Return info
        return info

    except(Exception, psycopg2.Error) as error:
        # Error handling
        print("error: " + error.pgerror)

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()


def get_table_schema():
    # SQL query to get a table schema including column name and data type
    query_get_table_schema = """SELECT table_name, column_name, data_type 
                                FROM information_schema.columns 
                                WHERE table_catalog = 'ai_playground' 
                                AND table_name = 'newa_weather';
                                """

    # Query the table
    schema = run_query(query_get_table_schema)

    # Print all rows
    for row in schema:
        print(row)

    print('\n')


def get_first_row(table_name, col_to_order):
    query_get_first_row_ascending = f"""
                                       SELECT *
                                       FROM {table_name}
                                       ORDER BY {col_to_order}
                                       LIMIT 1;
                                    """

    # Run the query on the given table name
    schema = run_query(query_get_first_row_ascending)

    # Print the results
    for row in schema:
        print(schema)

    print('\n')

def print_all_records(table_name):
    query_get_all_records = f"""
                              SELECT *
                              FROM {table_name};
                            """

    # Run the query
    records = run_query(query_get_all_records)

    # Print all records
    for row in records:
        print(row)

    print('\n')

# Call the function to print all records in the 'newa_weather' table
def add_to_newa(json_ob):
    json_ob = json.loads(json_ob)
    prcp = json_ob['dlyData'][0][1]
    maxt = json_ob['dlyData'][0][2]
    mint = json_ob['dlyData'][0][3]
    time_string = get_yesterday_timestamptz()

    query_insert_data = f"""
                            INSERT INTO newa_weather(time, prcp, max_temp, min_temp)
                            VALUES ({time_string},{prcp},{maxt},{mint});
                        """

    # Run the query
    run_query(query_insert_data)


def add_to_table():
    time_string = get_yesterday_timestamptz()
    prcp = 0.88
    maxt = 88.5
    mint = 56.7

    query_insert_data = f"""
                            INSERT INTO newa_weather(time, prcp, max_temp, min_temp)
                            VALUES ('{time_string}',{prcp},{maxt},{mint});
                        """

    # Run the query
    run_query(query_insert_data)


def newa_date_times():
    curr_date = date.today() - timedelta(days=1)
    edate = curr_date.strftime('%Y%m%d') + "00"
    curr_date = date.today() - timedelta(days=1)
    sdate = curr_date.strftime('%Y%m%d') + "00"
    return sdate, edate


def format_json(start, end):
    payload = {"sid": "in_con newa", "sdate": start, "edate": end, "extraelems": ""}
    # headers = {
    # "Content-Type": "application/json"
    #  }
    r = requests.post("https://hrly.nrcc.cornell.edu/stnHrly", json=payload, headers={'User-Agent': 'Mozilla/5.0'})
    print(r.status_code)
    print(r.text)

    res = r.json()
    fields = res["dlyFields"]
    values = res["dlyData"]

    dly_data = {
        "dlyFields": fields,
        "dlyData": values
    }

    json_obj = json.dumps(dly_data, indent=4)
    return json_obj


def get_yesterday_timestamptz():
    # Get the current time in UTC
    now = datetime.datetime.now(datetime.timezone.utc)

    # Subtract one day to get yesterday's date and time
    yesterday = now - datetime.timedelta(days=1)

    # Format the datetime to fit into a TIMESTAMPTZ column
    timestamptz_value = yesterday.isoformat()

    return f'{timestamptz_value}'

get_table_schema()
```

