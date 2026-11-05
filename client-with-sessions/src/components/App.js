
import React, { useEffect, useState } from "react";
import NavBar from "./NavBar";
import Login from "../pages/Login";
import Expenses from "./Expenses";

function App() {
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    fetch("/check_session")
      .then((response) => {
        if (!response.ok) {
          return null;
        }
        return response.json();
      })
      .then((userData) => {
        if (userData) {
          setUser(userData);
        }
      })
      .catch((error) => {
        console.error("Session check failed:", error);
      })
      .finally(() => {
        setCheckingSession(false);
      });
  }, []);

  if (checkingSession) {
    return <p>Checking your session...</p>;
  }

  if (!user) {
    return <Login onLogin={setUser} />;
  }

  return (
    <>
      <NavBar user={user} setUser={setUser} />
      <main>
        <p>You are logged in!</p>
        <Expenses />
      </main>
    </>
  );
}

export default App;

