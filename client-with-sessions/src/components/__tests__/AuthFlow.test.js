import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

jest.mock("../Expenses", () => () => null);

function jsonResponse(data, ok = true) {
  return Promise.resolve({
    ok,
    json: () => Promise.resolve(data),
  });
}

beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  delete global.fetch;
});

test("signup establishes the client session and logout returns to login", async () => {
  global.fetch
    .mockImplementationOnce(() => jsonResponse({}, false))
    .mockImplementationOnce(() =>
      jsonResponse({
        message: "Account created successfully",
        user: { id: 1, username: "test-user", email: "test@example.com" },
      })
    )
    .mockImplementationOnce(() =>
      jsonResponse({ message: "Logout successful" })
    );

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );

  fireEvent.click(await screen.findByRole("button", { name: "Sign Up" }));
  fireEvent.change(screen.getByLabelText("Username"), {
    target: { value: "test-user" },
  });
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "test@example.com" },
  });
  fireEvent.change(screen.getByLabelText("Password", { selector: "input" }), {
    target: { value: "password123" },
  });
  fireEvent.change(screen.getByLabelText("Password Confirmation"), {
    target: { value: "password123" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

  expect(await screen.findByText("You are logged in!")).toBeTruthy();
  expect(global.fetch).toHaveBeenNthCalledWith(
    2,
    "/signup",
    expect.objectContaining({
      method: "POST",
      body: JSON.stringify({
        username: "test-user",
        email: "test@example.com",
        password: "password123",
      }),
    })
  );

  fireEvent.click(screen.getByRole("button", { name: "Logout" }));
  expect(await screen.findByLabelText("Email")).toBeTruthy();
  await waitFor(() => expect(global.fetch).toHaveBeenCalledTimes(3));
});

test("login submits email and password and uses the returned user", async () => {
  global.fetch
    .mockImplementationOnce(() => jsonResponse({}, false))
    .mockImplementationOnce(() =>
      jsonResponse({
        message: "Login successful",
        user: { id: 2, username: "existing-user", email: "existing@example.com" },
      })
    );

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );

  fireEvent.change(await screen.findByLabelText("Email"), {
    target: { value: "existing@example.com" },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: "password123" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Login" }));

  expect(await screen.findByText("You are logged in!")).toBeTruthy();
  expect(global.fetch).toHaveBeenNthCalledWith(
    2,
    "/login",
    expect.objectContaining({
      method: "POST",
      body: JSON.stringify({
        email: "existing@example.com",
        password: "password123",
      }),
    })
  );
});

test("signup reports password mismatch without sending a request", async () => {
  global.fetch.mockImplementationOnce(() => jsonResponse({}, false));

  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );

  fireEvent.click(await screen.findByRole("button", { name: "Sign Up" }));
  fireEvent.change(screen.getByLabelText("Username"), {
    target: { value: "test-user" },
  });
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: "test@example.com" },
  });
  fireEvent.change(screen.getByLabelText("Password", { selector: "input" }), {
    target: { value: "password123" },
  });
  fireEvent.change(screen.getByLabelText("Password Confirmation"), {
    target: { value: "different123" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Sign Up" }));

  expect(await screen.findByText("Passwords do not match.")).toBeTruthy();
  expect(global.fetch).toHaveBeenCalledTimes(1);
});
