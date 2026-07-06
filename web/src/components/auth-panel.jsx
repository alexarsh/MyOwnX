import { useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth-context.jsx";
import { navigate } from "../router.jsx";

export default function AuthPanel() {
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
      const { access_token } =
        mode === "signup"
          ? await api.signup({
              ...form,
              display_name: form.display_name || form.username,
            })
          : await api.login({ username: form.username, password: form.password });
      await signIn(access_token);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-panel">
      <div className="tabs">
        <button
          className={mode === "signup" ? "tab active" : "tab"}
          onClick={() => setMode("signup")}
        >
          Create account
        </button>
        <button
          className={mode === "login" ? "tab active" : "tab"}
          onClick={() => setMode("login")}
        >
          Log in
        </button>
      </div>
      <form className="auth-form" onSubmit={submit}>
        <input
          value={form.username}
          onChange={set("username")}
          placeholder="username — lowercase, digits, _"
          aria-label="Username"
        />
        {mode === "signup" && (
          <input
            value={form.display_name}
            onChange={set("display_name")}
            placeholder="display name (optional)"
            aria-label="Display name"
          />
        )}
        <input
          type="password"
          value={form.password}
          onChange={set("password")}
          placeholder="password — at least 8 characters"
          aria-label="Password"
        />
        {error && <p className="form-error">{error}</p>}
        <button
          className="btn primary big block"
          disabled={busy || !form.username || !form.password}
        >
          {mode === "signup" ? "Join MyOwnX" : "Log in"}
        </button>
      </form>
    </div>
  );
}
