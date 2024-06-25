from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all rout
client = MongoClient('mongodb+srv://admin:1234@cluster1.evcobka.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1')
db = client.github_events

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        handle_event(event_type, data)
        return jsonify({'status': 'success'}), 200

def handle_event(event_type, data):
    if event_type == 'push':
        handle_push_event(data)
    elif event_type == 'pull_request':
        handle_pull_request_event(data)
    elif event_type == 'merge':
        handle_merge_event(data)

def handle_push_event(data):
    event = {
        "request_id": data['after'],  # Git commit hash
        "author": data['pusher']['name'],
        "action": "PUSH",
        "from_branch": "",  # No from_branch for push events
        "to_branch": data['ref'].split('/')[-1],
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    }
    db.events.insert_one(event)

def handle_pull_request_event(data):
    event = {
        "request_id": str(data['pull_request']['id']),
        "author": data['sender']['login'],
        "action": "PULL_REQUEST",
        "from_branch": data['pull_request']['head']['ref'],
        "to_branch": data['pull_request']['base']['ref'],
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    }
    db.events.insert_one(event)

def handle_merge_event(data):
    event = {
        "request_id": str(data['pull_request']['id']),
        "author": data['sender']['login'],
        "action": "MERGE",
        "from_branch": data['pull_request']['head']['ref'],
        "to_branch": data['pull_request']['base']['ref'],
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z'
    }
    db.events.insert_one(event)

@app.route('/api/events', methods=['GET'])
def get_events():
    events = list(db.events.find().sort('timestamp', -1).limit(10))
    print(events)
    for event in events:
        event['_id'] = str(event['_id'])
    return jsonify(events)

@app.route('/', methods=['GET'])
def home():
    return 'Working !'

if __name__ == '__main__':
    app.run(debug=True, port=5000)