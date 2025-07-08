import csv
import requests
import sqlite3

def match_and_save(api_endpoint, csv_filepath, csv_field='name', api_field='name', id_field='id', db_path='output.db'):
    # Read CSV file
    with open(csv_filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        csv_data = list(reader)

    # Fetch data from API
    response = requests.get(api_endpoint)
    response.raise_for_status()
    api_data = response.json()

    # Build a lookup from API field to internal ID
    api_lookup = {item[api_field]: item[id_field] for item in api_data}

    # Prepare data for saving
    matched_rows = []
    for row in csv_data:
        key = row[csv_field]
        internal_id = api_lookup.get(key)
        if internal_id is not None:
            matched_row = dict(row)
            matched_row['internal_id'] = internal_id
            matched_rows.append(matched_row)

    # Save to SQLite table
    if matched_rows:
        conn = sqlite3.connect(db_path)
        columns = list(matched_rows[0].keys())
        placeholders = ','.join('?' for _ in columns)
        table_name = 'matched_data'
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([col + ' TEXT' for col in columns])})")
        conn.executemany(
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
            [[row[col] for col in columns] for row in matched_rows]
        )
        conn.commit()
        conn.close()

# Example usage:
# match_and_save('https://api.example.com/items', 'data.csv')
