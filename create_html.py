import os

# Ensure the "templates" directory exists
os.makedirs("templates", exist_ok=True)

# HTML content to be written to the file
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mo Van and Man</title>
</head>
<body>
    <h1>Welcome to Mo Van and Man</h1>
    <button onclick="location.href='/add_order'">Add Order</button>
    <button onclick="location.href='/get_orders'">View Orders</button>
</body>
</html>
"""

# Write the HTML content to a file named "index.html" in the "templates" folder
with open("templates/index.html", "w") as file:
    file.write(html_content)

print("HTML file 'index.html' created successfully in the 'templates' folder!")
