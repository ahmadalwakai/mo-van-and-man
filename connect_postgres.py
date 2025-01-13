import psycopg2

try:
    # Connect to PostgreSQL
    connection = psycopg2.connect(
        host="127.0.0.1",       # Localhost
        port="5432",            # Default PostgreSQL port
        database="postgres",    # Default database
        user="postgres",        # Default superuser
        password="112233"       # Your provided password
    )
    print("✅ Connected to PostgreSQL successfully!")

    # Create a cursor object
    cursor = connection.cursor()

    # Execute a sample query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("PostgreSQL Version:", version)

except Exception as error:
    print("❌ Error connecting to PostgreSQL:", error)

finally:
    # Close the connection
    if 'connection' in locals() and connection:
        cursor.close()
        connection.close()
        print("🔒 PostgreSQL connection closed.")
