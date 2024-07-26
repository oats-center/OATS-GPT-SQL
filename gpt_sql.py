import requests
import json
import datetime
from datetime import date, timedelta
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)
table_catalog = "oats"
def run_query(input_query):
    # Connect to oats1.server.oats server
    # Requires tailscale to be active
    #CONNECTION = "postgresql://baile343:REmHzyBiFUu6rQ@@oats1.server.oats:5432/oats"
    #postgresql://username:password@oats1.server.oats:port_numer/database_name
    conn = psycopg2.connect(user="baile343",
                            password="REmHzyBiFUu6rQ@",
                            host="oats1.server.oats",
                            port="5432",
                            database="oats")

    #conn = None

    try:
        print("Connecting to purdue database...")

        # Create a connection with the database
        #conn = psycopg2.connect(CONNECTION)

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
        print("error: " + str(error))

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()


@app.route("/get_first_row/<table_name>/<col_to_order>", methods=["GET"])
def get_first_row(table_name, col_to_order):
    query_get_first_row_ascending = f"""
                                       SELECT *
                                       FROM {table_name}
                                       ORDER BY {col_to_order}
                                       LIMIT 1;
                                    """

    # Run the query on the given table name
    result = run_query(query_get_first_row_ascending)

    # Convert the result to JSON
    return jsonify(result)


@app.route("/run_query", methods=["POST"])
def run_query_api():
    input_query = request.json.get("query")
    result = run_query(input_query)
    return jsonify(result)


@app.route("/get_table_schema", methods=["GET"])
def get_table_schema_api():
    table_name = request.args.get('table_name')

    if not table_name:
        return jsonify({"error": "table_name is required"}), 400

    query_get_table_schema = f"""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_catalog = '{table_catalog}'
        AND table_name = '{table_name}';
    """

    # Query the table
    schema = run_query(query_get_table_schema)

    return jsonify(schema)


@app.route("/add_to_newa", methods=["POST"])
def add_to_newa_api():
    json_ob = request.json
    prcp = json_ob['dlyData'][0][1]
    maxt = json_ob['dlyData'][0][2]
    mint = json_ob['dlyData'][0][3]
    time_string = get_yesterday_timestamptz()

    query_insert_data = f"""
                            INSERT INTO newa_weather(time, prcp, max_temp, min_temp)
                            VALUES ('{time_string}',{prcp},{maxt},{mint});
                        """

    # Run the query
    run_query(query_insert_data)

    return jsonify({"status": "success"})


@app.route("/add_to_table", methods=["POST"])
def add_to_table_api():
    time_string = get_yesterday_timestamptz()
    prcp = request.json.get("prcp", 0.88)
    maxt = request.json.get("maxt", 88.5)
    mint = request.json.get("mint", 56.7)

    query_insert_data = f"""
                            INSERT INTO newa_weather(time, prcp, max_temp, min_temp)
                            VALUES ('{time_string}',{prcp},{maxt},{mint});
                        """

    # Run the query
    run_query(query_insert_data)

    return jsonify({"status": "success"})


@app.route("/newa_date_times", methods=["GET"])
def newa_date_times_api():
    curr_date = date.today() - timedelta(days=1)
    edate = curr_date.strftime('%Y%m%d') + "00"
    curr_date = date.today() - timedelta(days=1)
    sdate = curr_date.strftime('%Y%m%d') + "00"
    return jsonify({"sdate": sdate, "edate": edate})


@app.route("/format_json", methods=["POST"])
def format_json_api():
    start = request.json.get("start")
    end = request.json.get("end")
    payload = {"sid": "in_con newa", "sdate": start, "edate": end, "extraelems": ""}
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
    return jsonify(json.loads(json_obj))


@app.route("/get_yesterday_timestamptz", methods=["GET"])
def get_yesterday_timestamptz_api():
    now = datetime.datetime.now(datetime.timezone.utc)
    yesterday = now - datetime.timedelta(days=1)
    timestamptz_value = yesterday.isoformat()
    return jsonify({"timestamptz": timestamptz_value})


def get_yesterday_timestamptz():
    # Get the current time in UTC
    now = datetime.datetime.now(datetime.timezone.utc)

    # Subtract one day to get yesterday's date and time
    yesterday = now - datetime.timedelta(days=1)

    # Format the datetime to fit into a TIMESTAMPTZ column
    timestamptz_value = yesterday.isoformat()

    return f'{timestamptz_value}'


@app.route("/get_data_from_time_range", methods=["POST"])
def get_data_from_time_range():
    table_name = request.json.get("table_name")
    start_time = request.json.get("start_time")
    end_time = request.json.get("end_time")

    query = f"""
             SELECT *
             FROM {table_name}
             WHERE time >= '{start_time}' AND time <= '{end_time}';
             """

    result = run_query(query)
    return jsonify(result)


@app.route("/get_max/<table_name>/<column_name>", methods=["GET"])
def get_max(table_name, column_name):
    query = f"""
             SELECT MAX({column_name})
             FROM {table_name};
             """

    result = run_query(query)
    return jsonify(result)

@app.route("/get_min/<table_name>/<column_name>", methods=["GET"])
def get_min(table_name, column_name):
    query = f"""
             SELECT MIN({column_name})
             FROM {table_name};
             """

    result = run_query(query)
    return jsonify(result)


@app.route("/get_avg/<table_name>/<column_name>", methods=["GET"])
def get_avg(table_name, column_name):
    query = f"""
             SELECT AVG({column_name})
             FROM {table_name};
             """

    result = run_query(query)
    return jsonify(result)

@app.route("/execute_custom_query", methods=["POST"]) #This will be the one that chat gpt creates itself and then calls
def execute_custom_query():
    input_query = request.json.get("query")
    result = run_query(input_query)
    return jsonify(result)

if __name__ =="__main__":
    app.run(debug=True)
