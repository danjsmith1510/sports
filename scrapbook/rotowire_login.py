import requests

# Start a session to persist cookies
session = requests.Session()

# Replace with your actual credentials
login_url = "https://www.rotowire.com/subscribe/buy-flow/api/login.php"
payload = {
    'username': 'danieljsmith1510',
    'password': 'Ernie2025'
}

# Log in
response = session.post(login_url, data=payload)

print (response.text)

# # Optional: Check if login was successful by verifying content
# if "My Account" in response.text or response.url.endswith("/myaccount.php"):
#     print("Login successful")
# else:
#     print("Login failed or redirected elsewhere")