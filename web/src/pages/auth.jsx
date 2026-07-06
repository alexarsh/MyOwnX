import { useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth-context.jsx";
import { navigate } from "../router.jsx";

export default function Auth() {
  const { signIn } = useAuth();
  const [mode, setMode] = useState("signup");
  const [form, setForm] = useState({ username: "", display_name: "", password: "" });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const call = mode === "signup" ? api.signup(form) : api.login(form);
      const { access_token } = await call;
      await signIn(access_token);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-page">
      <h1 className="page-title">
        {mode === "signup" ? "Claim your handle" : "Welcome back"}
      </h1>
      <div className="tabs">
        <button
          className={mode === "signup" ? "tab active" : "tab"}
          onClick={() => setMode("signup")}
        >
          Sign up
        </button>
        <button
          className={mode === "login" ? "tab active" : "tab"}
          onClick={() => setMode("login")}
        >
          Log in
        </button>
      </div>
      <form className="auth-form" onSubmit={submit}>
        <label>
          Username
          <input
            value={form.username}
            onChange={set("username")}
            placeholder="lowercase, digits, _"
            autoFocus
          />
        </label>
        {mode === "signup" && (
          <label>
            Display name
            <input
              value={form.display_name}
              onChange={set("display_name")}
              placeholder="How you'll appear"
            />
          </label>
        )}
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={set("password")}
            placeholder="At least 8 characters"
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <button className="btn primary big" disabled={busy}>
          {mode === "signup" ? "Create account" : "Log in"}
        </button>
      </form>
    </div>
  );
}
