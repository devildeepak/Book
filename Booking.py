from flask import Flask, render_template_string, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# User options
users = {
    "Vyshnavi Guptha": {
        "name": "Vyshnavi Guptha",
        "userId": "86626a3e-8cf2-4f61-a34e-63869de1214d",
        "mobile": "9788816044",
        "email": "fadaw50425@exclussi.com"
    },
    "Karthik S": {
        "name": "Karthik S",
        "userId": "22183f18-dfaa-4eca-a3d1-003116f785f0",
        "mobile": "9347134395",
        "email": "karthiksamana@gmail.com"
    }
}

# Venue options
venues = {
    "Court 2 (SP8)": {
        "venueId": "450484a0-ba5d-4c5d-a55b-f4c71eb5d59e",
        "sportId": "SP8",
        "courtName": " Court 2",
        "courtId": "20603",
        "courtBrother": [20602, 20604]
    },
    "Turf 1 (SP2)": {
        "venueId": "f4e3de93-ec8f-4f93-8c45-0e12c8c2ef4c",
        "sportId": "SP2",
        "courtName": " Turf 1",
        "courtId": "20461",
        "courtBrother": [20462, 20463, 20464]
    }
}

form_template = '''
<!doctype html>
<html>
<head>
    <title>Slot Booker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <script>
        function addBookingBlock() {
            let container = document.getElementById("bookings");
            let first = container.querySelector('.booking-block');
            let clone = first.cloneNode(true);

            clone.querySelectorAll("input, select").forEach(el => {
                if (el.tagName === 'SELECT') el.selectedIndex = 0;
                else el.value = '';
            });

            container.appendChild(clone);
        }

        function removeBlock(button) {
            let container = document.getElementById("bookings");
            let block = button.closest('.booking-block');
            if (container.children.length > 1) {
                container.removeChild(block);
            } else {
                alert("At least one booking is required.");
            }
        }
    </script>
</head>
<body class="bg-success bg-opacity-10">
<div class="container mt-5">
    <h2 class="mb-4 text-success">Slot Booker</h2>
    <form method="POST">
        <div id="bookings">
            <div class="booking-block mb-4 border rounded p-3 bg-white position-relative">
                <button type="button" class="btn-close position-absolute top-0 end-0 m-3" aria-label="Close" onclick="removeBlock(this)"></button>

                <div class="mb-3">
                    <label class="form-label text-success">Select User</label>
                    <select name="user" class="form-select" required>
                        {% for user in users %}
                            <option value="{{ user }}">{{ user }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label text-success">Select Venue</label>
                    <select name="venue" class="form-select" required>
                        {% for venue in venues %}
                            <option value="{{ venue }}">{{ venue }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label text-success">Date</label>
                    <input name="date" class="form-control" type="date" required>
                </div>
                <div class="mb-3">
                    <label class="form-label text-success">Start Time (HH:MM:SS)</label>
                    <input name="start_time" class="form-control" type="text" required>
                </div>
                <div class="mb-3">
                    <label class="form-label text-success">Number of 30-min Slots</label>
                    <input name="num_slots" class="form-control" type="number" required>
                </div>
            </div>
        </div>
        <button type="button" class="btn btn-outline-success mb-3" onclick="addBookingBlock()">+ Add Another Booking</button><br>
        <button class="btn btn-success">Submit Bookings</button>
    </form>
    {% if result %}
        <div class="alert mt-4 {{ 'alert-success' if success else 'alert-danger' }}">
            {{ result|safe }}
        </div>
    {% endif %}
</div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    success = False
    if request.method == 'POST':
        data = request.form.to_dict(flat=False)
        num_bookings = len(data['user'])
        responses = []

        for i in range(num_bookings):
            user = users[data['user'][i]]
            venue = venues[data['venue'][i]]
            date = data['date'][i]
            start_time_input = data['start_time'][i]
            num_slots = int(data['num_slots'][i])

            start_time = datetime.strptime(start_time_input, "%H:%M:%S")
            all_slots = []
            for j in range(num_slots):
                slot_time = (start_time + timedelta(minutes=30 * j)).strftime("%H:%M:%S")
                mins = (start_time + timedelta(minutes=30 * j)).hour * 60 + (start_time + timedelta(minutes=30 * j)).minute
                slot = {
                    "status": 1,
                    "price": "550.0",
                    "time": slot_time,
                    "mins": mins,
                    "courtName": venue["courtName"],
                    "courtId": venue["courtId"],
                    "durationInMin": 30,
                    "date": date,
                    "sportId": venue["sportId"],
                    "maxSlots": 4,
                    "closeTime": 1440,
                    "courtBrother": venue["courtBrother"],
                    "count": 1,
                    "id": 1
                }
                all_slots.append(slot)

            def chunk_slots(slots, size=4):
                for k in range(0, len(slots), size):
                    yield slots[k:k+size]

            headers = {
                "sec-ch-ua-platform": "Windows",
                "Authorization": "b4ee93df154de37b0e38aa6a5dfda071aa751bfa",
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
                "Content-Type": "application/json",
                "sec-ch-ua-mobile": "?0",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "host": "playo.club"
            }

            for batch in chunk_slots(all_slots, 4):
                payload = {
                    **user,
                    "countryCode": "+91",
                    "coupon": "T5PTP100",
                    "eventId": "notavailable",
                    "extras": [],
                    "deviceType": 99,
                    "karma": 0,
                    "full": 0,
                    "bookType": 0,
                    "paidAmount": 0,
                    "payableAtVenue": 0,
                    "insurance": False,
                    "venueId": venue["venueId"],
                    "sportId": venue["sportId"],
                    "slots": batch,
                    "webVersion": 2
                }

                try:
                    res = requests.post("https://playo.club/book-api/v14/booking/", headers=headers, json=payload)
                    responses.append(f"<strong>{user['name']} @ {venue['courtName']}</strong><br>Status: {res.status_code}<br>{res.text}<hr>")
                    if res.status_code == 200:
                        success = True
                except Exception as e:
                    responses.append(f"<strong>Error:</strong> {str(e)}<hr>")
                    success = False

        result = "<br>".join(responses)

    return render_template_string(form_template, users=users, venues=venues, result=result, success=success)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
