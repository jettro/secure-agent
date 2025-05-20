import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'http://localhost:8080/', // Change if your Keycloak runs elsewhere
  realm: 'local-dev',           // Your Keycloak realm
  clientId: 'fastapi-client',       // Your Keycloak client (should match what FastAPI uses)
});

export default keycloak;