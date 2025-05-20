import {createRoot} from 'react-dom/client'
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css'
import {ReactKeycloakProvider} from "@react-keycloak/web";
import keycloak from "./auth/keycloak.ts";
import App from './App'
import ErrorBoundary from "./ErrorBoundary.tsx";

createRoot(document.getElementById('root')!).render(
    <ReactKeycloakProvider authClient={keycloak}>
        <ErrorBoundary>
            <App/>
        </ErrorBoundary>
    </ReactKeycloakProvider>
)
