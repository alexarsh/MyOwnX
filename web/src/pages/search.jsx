import { useEffect, useState } from "react";

import { api } from "../api.js";
import Avatar from "../components/avatar.jsx";
import PostCard from "../components/post-card.jsx";
import { Link } from "../router.jsx";

export default function Search() {
  const [q, setQ] = useState("");
  const [type, setType] = useState("posts");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const query = q.trim();
    if (!query) return setResults(null);
    const timer = setTimeout(() => {
      api
        .search(query, type)
        .then(setResults)
        .catch((err) => setError(err.message));
    }, 250); // debounce keystrokes
    return () => clearTimeout(timer);
  }, [q, type]);

  return (
    <>
      <h2 className="page-title">Search</h2>
      <input
        className="search-input"
        value={q}
        onChange={(event) => setQ(event.target.value)}
        placeholder="Search posts and people…"
        autoFocus
      />
      <div className="tabs">
        {["posts", "users"].map((t) => (
          <button
            key={t}
            className={type === t ? "tab active" : "tab"}
            onClick={() => setType(t)}
          >
            {t === "posts" ? "Posts" : "People"}
          </button>
        ))}
      </div>
      {error && <p className="state-msg">{error}</p>}
      {results?.posts &&
        (results.posts.length ? (
          results.posts.map((post) => <PostCard key={post.id} post={post} />)
        ) : (
          <p className="state-msg">No posts match.</p>
        ))}
      {results?.users &&
        (results.users.length ? (
          results.users.map((user) => (
            <Link key={user.id} to={`/u/${user.username}`} className="user-card">
              <Avatar username={user.username} />
              <div>
                <strong>{user.display_name}</strong>
                <p className="post-meta">@{user.username}</p>
              </div>
            </Link>
          ))
        ) : (
          <p className="state-msg">No people match.</p>
        ))}
    </>
  );
}
