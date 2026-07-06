import { useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth-context.jsx";
import Avatar from "./avatar.jsx";

const MAX = 280;

export default function Composer({ replyTo = null, onPosted, placeholder }) {
  const { me } = useAuth();
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  if (!me) return null;
  const left = MAX - text.length;

  const submit = async (event) => {
    event.preventDefault();
    if (!text.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const post = await api.createPost({ text: text.trim(), reply_to_id: replyTo });
      setText("");
      onPosted?.(post);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="composer" onSubmit={submit}>
      <Avatar username={me.username} />
      <div className="composer-body">
        <textarea
          value={text}
          maxLength={MAX}
          placeholder={placeholder || "What's happening?"}
          onChange={(event) => setText(event.target.value)}
          rows={replyTo ? 2 : 3}
        />
        {error && <p className="form-error">{error}</p>}
        <div className="composer-row">
          <span className={`char-count ${left < 30 ? "warn" : ""}`}>{left}</span>
          <button className="btn primary" disabled={!text.trim() || busy}>
            {replyTo ? "Reply" : "Post"}
          </button>
        </div>
      </div>
    </form>
  );
}
