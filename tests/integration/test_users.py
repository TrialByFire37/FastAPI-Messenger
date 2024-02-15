# import json
# from fastapi.testclient import TestClient
# from src.app import app
#
# client = TestClient(app)
#
#
# # Endpoint: Get User Me
# def test_successful_get_user_me():
#     login_data = {
#         "username": "gelo21region",
#         "password": "string1"
#     }
#     response = client.post("/api/auth/jwt/login", data=login_data)
#     assert response.status_code == 200
#     assert "access_token" in response.json()
#     assert "token_type" in response.json()
#
#     token = response.json()['access_token']
#
#     headers = {
#         "Authorization": "Bearer " + str(token)
#     }
#     response = client.get("/api/user/me", headers=headers)
#     assert response.status_code == 200
#     assert "username" in response.json()
#     assert "email" in response.json()
#     assert "is_active" in response.json()
#     assert "is_superuser" in response.json()
#
#
# def test_unauthorized_get_user_me():
#     response = client.get("/api/user/me")
#     assert response.status_code == 401
#
#
# def test_invalid_token_get_user_me():
#     headers = {
#         "Authorization": "Bearer invalid_token"
#     }
#     response = client.get("/api/user/me", headers=headers)
#     assert response.status_code == 401
