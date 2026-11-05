import React, { useCallback, useEffect, useState } from "react";
import { Button, Error, FormField, Input, Label } from "../styles";

const EMPTY_FORM = { title: "", amount: "", category: "" };

function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");

  const loadExpenses = useCallback(() => {
    fetch("/expenses")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data) => setExpenses(data.items))
      .catch(() => setError("Could not load expenses"));
  }, []);

  useEffect(loadExpenses, [loadExpenses]);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function handleSubmit(e) {
    e.preventDefault();
    setError("");
    fetch("/expenses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, amount: Number(form.amount) }),
    }).then((r) =>
      r.json().then((data) => {
        if (r.ok) {
          setForm(EMPTY_FORM);
          loadExpenses();
        } else {
          setError(data.error || "Could not add expense");
        }
      })
    );
  }

  function handleDelete(id) {
    fetch(`/expenses/${id}`, { method: "DELETE" }).then((r) => {
      if (r.ok) {
        loadExpenses();
      } else {
        setError("Could not delete expense");
      }
    });
  }

  return (
    <div style={{ maxWidth: 600, margin: "16px auto", padding: "0 16px" }}>
      <h2>Expense Tracker</h2>
      <form onSubmit={handleSubmit}>
        <FormField>
          <Label htmlFor="title">Title</Label>
          <Input id="title" name="title" value={form.title} onChange={handleChange} required />
        </FormField>
        <FormField>
          <Label htmlFor="amount">Amount</Label>
          <Input
            id="amount"
            name="amount"
            type="number"
            step="0.01"
            min="0.01"
            value={form.amount}
            onChange={handleChange}
            required
          />
        </FormField>
        <FormField>
          <Label htmlFor="category">Category</Label>
          <Input id="category" name="category" value={form.category} onChange={handleChange} required />
        </FormField>
        <FormField>
          <Button type="submit">Add expense</Button>
        </FormField>
        {error && <Error>{error}</Error>}
      </form>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {expenses.map((x) => (
          <li
            key={x.id}
            style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #ddd" }}
          >
            <span>
              {x.title} ({x.category}) -{" "}
              {Number(x.amount).toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
            <Button variant="outline" onClick={() => handleDelete(x.id)}>
              Delete
            </Button>
          </li>
        ))}
        {expenses.length === 0 && <li>No expenses yet.</li>}
      </ul>
    </div>
  );
}

export default Expenses;
