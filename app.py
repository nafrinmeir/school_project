from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://mongo:27017/")
db = client.weekly_planner
collection = db.schedule

@app.route('/', methods=['GET', 'POST'])
def index():
    now = datetime.now()
    week_offset = int(request.args.get('week_offset', 0))
    start_of_week = now - timedelta(days=(now.weekday() + 1) % 7) + timedelta(weeks=week_offset)
    
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    hours = [f"{hour}:00" for hour in range(7, 18)]
    subjects = ["Math", "Science", "History", "Geography", "Art", "Music", "PE", "Computer Science", "Literature", "Physics"]

    # Load schedule from MongoDB
    schedule = {date.strftime('%Y-%m-%d'): {hour: None for hour in hours} for date in week_dates}
    for entry in collection.find({"date": {"$in": [d.strftime('%Y-%m-%d') for d in week_dates]}}):
        schedule[entry["date"]][entry["hour"]] = entry["subject"]

    if request.method == 'POST':
        selected_subject = request.form.get('subject')
        selected_date = request.form.get('date')
        selected_hour = request.form.get('hour')

        # Update the database
        collection.update_one(
            {"date": selected_date, "hour": selected_hour},
            {"$set": {"subject": selected_subject}},
            upsert=True
        )

        return jsonify({"message": "Schedule updated"}), 200

    return render_template('calendar.html', week_dates=week_dates, hours=hours, now=now, subjects=subjects, schedule=schedule, week_offset=week_offset)

# API Routes
@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """ Fetch all scheduled subjects from MongoDB. """
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data), 200

@app.route('/api/schedule', methods=['POST'])
def add_schedule():
    """ Add or update a schedule entry via API. """
    data = request.json
    if not data or "date" not in data or "hour" not in data or "subject" not in data:
        return jsonify({"error": "Invalid input"}), 400

    collection.update_one(
        {"date": data["date"], "hour": data["hour"]},
        {"$set": {"subject": data["subject"]}},
        upsert=True
    )
    return jsonify({"message": "Schedule updated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

