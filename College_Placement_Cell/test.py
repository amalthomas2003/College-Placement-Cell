

from flask import Flask, render_template, request, redirect
import mysql.connector
import base64

app = Flask(__name__)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "careerconnect",
    "database": "maindb"
}


# Connect to MySQL
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Create a table to store image data
create_table_query = """
CREATE TABLE IF NOT EXISTS images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_data MEDIUMBLOB
)
"""
cursor.execute(create_table_query)
conn.commit()

# Close the connection after creating the table
cursor.close()
conn.close()


@app.route('/')
def index():
    # Fetch the latest image from the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT image_data FROM images ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    # Convert image data to base64 encoding
    image_base64 = base64.b64encode(result[0]).decode('utf-8') if result else None

    return render_template('test.html', image_base64=image_base64)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect('/')
    
    file = request.files['file']

    if file.filename == '':
        return redirect('/')

    # Read image data
    image_data = file.read()

    # Save image data to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images (image_data) VALUES (%s)", (image_data,))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
