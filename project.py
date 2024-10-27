import http.server
import socketserver
import datetime
import pytz
import threading
import time
import urllib.parse
import json

# Set the timezone to India
india_tz = pytz.timezone('Asia/Kolkata')

# List to store medicine reminders
medicine_reminders = []

def reminder_thread():
    while True:
        now = datetime.datetime.now(india_tz)
        for name, medHour, medMin in medicine_reminders:
            if medHour == now.hour and medMin == now.minute:
                notification = f"It's time to take your {name}!"
                print(notification)  # You could log this or use a different notification system
        time.sleep(30)  # Sleep for 30 seconds

# Start the reminder thread
threading.Thread(target=reminder_thread, daemon=True).start()

class ReminderHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path.startswith('/api/reminders'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(medicine_reminders).encode())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/add_reminder':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.add_reminder(urllib.parse.parse_qs(post_data.decode()))
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

    def get_html(self):
        return f"""
        <html>
        <head>
            <title>Medicine Reminder</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f0f8ff;
                    color: #333;
                }}
                h1 {{
                    color: #4CAF50;
                    text-align: center;
                }}
                h2 {{
                    color: #333;
                }}
                form {{
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }}
                label {{
                    display: block;
                    margin: 10px 0 5px;
                }}
                input, select {{
                    width: calc(100% - 20px);
                    padding: 10px;
                    margin-bottom: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }}
                button {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
                ul {{
                    list-style-type: none;
                    padding: 0;
                }}
                li {{
                    background-color: #e7f3fe;
                    margin: 5px 0;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
                }}
                .notification {{
                    color: red;
                    font-weight: bold;
                    margin-top: 20px;
                }}
            </style>
            <script>
                function checkReminders() {{
                    fetch('/api/reminders')
                        .then(response => response.json())
                        .then(data => {{
                            const now = new Date();
                            data.forEach(reminder => {{
                                const reminderHour = reminder[1];
                                const reminderMinute = reminder[2];
                                if (reminderHour === now.getHours() && reminderMinute === now.getMinutes()) {{
                                    alert('Time to take your ' + reminder[0] + '!');
                                }}
                            }});
                        }});
                }}
                setInterval(checkReminders, 60000); // Check every minute
            </script>
        </head>
        <body>
            <h1>Medicine Reminder</h1>
            <form action="/add_reminder" method="post">
                <label for="med_name">Medicine Name:</label>
                <input type="text" id="med_name" name="med_name" required>
                <label for="med_hour">Hour (1-12):</label>
                <input type="number" id="med_hour" name="med_hour" min="1" max="12" required>
                <label for="med_min">Minutes (0-59):</label>
                <input type="number" id="med_min" name="med_min" min="0" max="59" required>
                <label for="med_am">AM/PM:</label>
                <select id="med_am" name="med_am">
                    <option value="am">AM</option>
                    <option value="pm">PM</option>
                </select>
                <button type="submit">Add Reminder</button>
            </form>

            <h2>Current Reminders:</h2>
            <ul>
                {self.list_reminders()}
            </ul>
        </body>
        </html>
        """

    def list_reminders(self):
        items = ""
        for name, hour, minute in medicine_reminders:
            items += f"<li>{name}: {hour:02}:{minute:02}</li>"
        return items

    def add_reminder(self, data):
        med_name = data['med_name'][0]
        med_hour = int(data['med_hour'][0])
        med_min = int(data['med_min'][0])
        med_am = data['med_am'][0]

        # Convert hour to 24-hour format
        if med_am == "pm" and med_hour != 12:
            med_hour += 12
        elif med_am == "am" and med_hour == 12:
            med_hour = 0

        medicine_reminders.append((med_name, med_hour, med_min))
        print(f"Reminder set for {med_name} at {med_hour:02}:{med_min:02}.")

# Set up the server
PORT = 8000
with socketserver.TCPServer(("", PORT), ReminderHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
