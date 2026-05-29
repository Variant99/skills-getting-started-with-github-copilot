from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["description"] == original_activities[expected_activity]["description"]


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "newstudent@mergington.edu"
    params = {"email": participant_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 200
    assert participant_email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {participant_email} for {activity_name}"


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"
    params = {"email": duplicate_email}
    original_count = activities[activity_name]["participants"].count(duplicate_email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(duplicate_email) == original_count


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    params = {"email": "user@mergington.edu"}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    params = {"email": participant_email}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "unknown@mergington.edu"
    params = {"email": participant_email}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
