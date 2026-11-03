
import React, { useState } from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";
import { Button } from "../styles";

function NavBar({ user, setUser }) {
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  function handleLogoutClick() {
    setIsLoggingOut(true);

    fetch("/logout", { method: "DELETE" })
      .then((response) => {
        if (response.ok) {
          setUser(null);
        } else {
          alert("Logout failed. Please try again.");
        }
      })
      .catch(() => {
        alert("Unable to connect to the server.");
      })
      .finally(() => {
        setIsLoggingOut(false);
      });
  }

  return (
    <Wrapper>
      <Logo>
        <Link to="/">My App</Link>
      </Logo>

      <Nav>
        <Button>Do Something</Button>

        <Button
          variant="outline"
          onClick={handleLogoutClick}
          disabled={isLoggingOut}
        >
          {isLoggingOut ? "Logging out..." : "Logout"}
        </Button>
      </Nav>
    </Wrapper>
  );
}

const Wrapper = styled.header`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 8px;
`;

const Logo = styled.h1`
  font-family: "Permanent Marker", cursive;
  font-size: 3rem;
  color: deeppink;
  margin: 0;
  line-height: 1;

  a {
    color: inherit;
    text-decoration: none;
  }
`;

const Nav = styled.nav`
  display: flex;
  gap: 4px;
  position: absolute;
  right: 8px;
`;

export default NavBar;
