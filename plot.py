def generate_machine_status_image():
    with psycopg2.connect(db_url, sslmode='require') as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT status FROM machine_status;')
                json.loads(cur.fetchone()[0])
                