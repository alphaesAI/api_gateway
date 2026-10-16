import requests

def get_auth_token(url, client_id, client_secret):

  # Encode the client ID and client secret
  headers = {
      "Content-Type": "application/x-www-form-urlencoded"
  }
  body = {
      "grant_type": "client_credentials",
      "client_id": client_id,
      "client_secret": client_secret
  }

  response = requests.post(url, data=body, headers=headers)
  return response.json()


if __name__ == "__main__":
    token = get_auth_token(
        "https://api.staging.medplum.dev/oauth2/token",
        "e3d2fd3e-4af1-46ae-9875-41e178a0c396",
        "3f60fedf974952b2b48d517e9144ce4dd4c238b909edb128fb4469fbcab79f54",
    )
    print(token)