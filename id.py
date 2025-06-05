import json
import logging
from datetime import datetime

# Define the path for user activity JSON
USER_ACTIVITY_FILE = 'user_activity.json'

# Load or initialize user activity data
def load_user_activity():
    try:
        # Try loading existing data if the file exists
        with open(USER_ACTIVITY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, return an empty dictionary
        logging.warning(f"{USER_ACTIVITY_FILE} not found. Creating a new one.")
        return {}

# Save user activity data to the JSON file
def save_user_activity(activity_data):
    try:
        with open(USER_ACTIVITY_FILE, 'w') as file:
            json.dump(activity_data, file, indent=4)
        logging.info(f"{USER_ACTIVITY_FILE} saved successfully.")
    except Exception as e:
        logging.error(f"Error saving {USER_ACTIVITY_FILE}: {e}")

def test_json_creation():
    # Load or initialize activity data
    activity_data = load_user_activity()

    # Create a test user activity entry
    test_user = "test_user"
    activity_entry = {
        "timestamp": datetime.now().isoformat(),
        "message": "Test message for JSON update",
        "flagged_keywords": ["drug"],
        "suspicion_level": "Suspicious",
        "alerted": False
    }

    # Initialize the user's activity if not already there
    if test_user not in activity_data:
        activity_data[test_user] = []

    # Add the test entry
    activity_data[test_user].append(activity_entry)

    # Save the updated activity data
    save_user_activity(activity_data)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_json_creation()
