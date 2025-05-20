# Secure Agents

## Initialise the local Keycloak 
We use Docker to run Keycloak locally. You can start it with the following command:

```bash
docker compose up -d
```
This will start Keycloak on port 8080. You can access the Keycloak admin console at `http://localhost:8080/auth/admin/` with the username `admin` and password `admin`.

### Create a new realm
1. Go to the Keycloak admin console at `http://localhost:8080/auth/admin/`.
2. Log in with the username `admin` and password `admin`.
3. Click on the "Add realm" button.
4. Enter a name for the realm (e.g. `local-dev`) and click "Create".
5. Click on the "Clients" tab in the left sidebar.
6. Click on the "Create" button.
7. Enter a name for the client (e.g. `fastapi-client`) and select "openid-connect" as the client protocol.
8. Valid redirect urls: `http://localhost:8000/docs/oauth2-redirect`
9. Web origins: `http://localhost:8000`
10. Click "Save".
11. Create a new user
12. Click on the "Users" tab in the left sidebar.
13. Click on the "Add user" button.
14. Enter a username (e.g. `jettro`) and click "Save".
15. Click on the "Credentials" tab.
16. Set a password for the user (e.g. `test`) and click "Set Password".
17. Make sure to set "Temporary" to "Off" so the user can log in with the password you just set.

Interesting blog post that might be usefull in the future:
https://darkaico.medium.com/building-a-secure-authentication-system-with-keycloak-react-and-flask-35aeee04e37a



## Running the application

# TODO
- Implement Axios interceptor to add the access token to the request headers
- Add a second application for the Agent to use
- Add the agent in the service to answer the question of the user.
- 