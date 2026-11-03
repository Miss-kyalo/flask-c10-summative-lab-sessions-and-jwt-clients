
import React, { useState } from "react";
import { Button, Error, Input, FormField, Label } from "../styles";

function SignUpForm({ onLogin }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirmation, setPasswordConfirmation] = useState("");
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    setErrors([]);

    if (password !== passwordConfirmation) {
      setErrors(["Passwords do not match."]);
      return;
    }

    setIsLoading(true);

    fetch("/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    })
      .then((r) => r.json().then((data) => ({ ok: r.ok, data })))
      .then(({ ok, data }) => {
        if (ok) {
          setIsLoading(false);
          onLogin(data.user);
        } else {
          setErrors([data.error || "Signup failed. Please try again."]);
          setIsLoading(false);
        }
      })
      .catch(() => {
        setErrors(["Unable to connect to the server."]);
        setIsLoading(false);
      });
  }

  return (
    <form onSubmit={handleSubmit}>
      <FormField>
        <Label htmlFor="username">Username</Label>
        <Input
          type="text"
          id="username"
          autoComplete="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </FormField>

      <FormField>
        <Label htmlFor="email">Email</Label>
        <Input
          type="email"
          id="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </FormField>

      <FormField>
        <Label htmlFor="password">Password</Label>
        <Input
          type="password"
          id="password"
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </FormField>

      <FormField>
        <Label htmlFor="password_confirmation">
          Password Confirmation
        </Label>
        <Input
          type="password"
          id="password_confirmation"
          autoComplete="new-password"
          value={passwordConfirmation}
          onChange={(e) => setPasswordConfirmation(e.target.value)}
          required
        />
      </FormField>

      <FormField>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Loading..." : "Sign Up"}
        </Button>
      </FormField>

      <FormField>
        {errors.map((err) => (
          <Error key={err}>{err}</Error>
        ))}
      </FormField>
    </form>
  );
}

export default SignUpForm;
