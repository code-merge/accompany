from app.tests.conftest import client  # Explicitly import the client fixture

def test_welcome_page(client):
    """
    Validates that the onboarding welcome page loads correctly.

    Asserts:
    --------
    - Returns HTTP 200 OK.
    - Contains expected onboarding text: "Your Business Companion".
    """
    res = client.get("/onboarding/")
    assert res.status_code == 200
    assert "Your Business Companion" in res.text

def test_licence_accept(client):
    """
    Ensures that the licence acceptance endpoint responds successfully.

    Behavior:
    ---------
    - Sends a GET request with `accept=true` query parameter.
    - Updates session acceptance flag (indirectly tested).

    Asserts:
    --------
    - Response status code is 200 OK.
    """
    res = client.get("/onboarding/licence?accept=true")
    assert res.status_code == 200

def test_db_standard_post_invalid(client):
    """
    Tests validation logic for the standard DB setup form submission.

    Behavior:
    ---------
    - Sends a POST request with an empty `db_name` field.

    Asserts:
    --------
    - Response status code is 200 OK (form re-render).
    - Response contains validation error message: "Database name is required".
    """
    res = client.post("/onboarding/db-setup/standard", data={"db_name": ""})
    assert res.status_code == 200
    assert "Database name is required" in res.text

def test_admin_user_post_invalid(client):
    """
    Validates admin user form error handling when inputs are invalid.

    Behavior:
    ---------
    - Sends a POST request with:
        - Blank full name
        - Invalid email
        - Short password
        - Mismatched confirmation

    Asserts:
    --------
    - Response status code is 200 OK (form re-render).
    - Response contains validation error: "Full name is required".
    """
    res = client.post("/onboarding/admin-user-setup", data={
        "full_name": "",
        "email": "bademail",
        "password": "short",
        "confirm_password": "nomatch"
    })
    assert res.status_code == 200
    assert "Full name is required" in res.text
