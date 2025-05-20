import { useKeycloak } from '@react-keycloak/web';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';

import React from 'react';
import { useAxiosAuth } from './auth/useAxiosAuth';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { keycloak } = useKeycloak();
  return keycloak.authenticated ? <>{children}</> : <Navigate to="/" replace />;
}

function App() {
  const { keycloak, initialized } = useKeycloak();
  useAxiosAuth();

  if (!initialized) return <div>Loading...</div>;

  return (
    <Router>
      <nav className="navbar navbar-expand navbar-light bg-light mb-3 fixed-top">
        <div className="container">
          <Link className="navbar-brand" to="/">MyApp</Link>
          <ul className="navbar-nav">
            <li className="nav-item"><Link className="nav-link" to="/">Home</Link></li>
            {keycloak.authenticated ? (
              <>
                <li className="nav-item"><Link className="nav-link" to="/dashboard">Dashboard</Link></li>
                <li className="nav-item">
                  <button className="btn btn-link nav-link" onClick={() => keycloak.logout()}>Logout</button>
                </li>
              </>
            ) : (
              <li className="nav-item">
                <button className="btn btn-link nav-link" onClick={() => keycloak.login()}>Login</button>
              </li>
            )}
          </ul>
        </div>
      </nav>
      <div className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard
                    user={keycloak.tokenParsed?.preferred_username || 'Unknown'}
                    token={keycloak.token || ''}
                />
              </PrivateRoute>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;