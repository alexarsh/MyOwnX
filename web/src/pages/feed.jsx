import { useCallback, useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth-context.jsx";
import Composer from "../components/composer.jsx";
import PostList from "../components/post-list.jsx";
import { Link } from "../router.jsx";

export default function Feed() {
  const { me, loading } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchPage = useCallback((cursor) => api.timeline(cursor), []);

  if (loading) return <p className="state-msg">Loading…</p>;

  if (!me) {
    return (
      <div className="hero">
        <h1 className="hero-title">
          Say it <em>loud.</em>
        </h1>
        <p className="hero-sub">
          MyOwnX is a tiny, fast corner of the internet. Post in 280
          characters, follow interesting people, own your feed.
        </p>
        <Link to="/auth" className="btn primary big">
          Create your account
        </Link>
      </div>
    );
  }

  return (
    <>
      <h2 className="page-title">Home</h2>
      <Composer onPosted={() => setRefreshKey((k) => k + 1)} />
      <PostList
        key={refreshKey}
        fetchPage={fetchPage}
        emptyText="Your feed is empty — follow people or write your first post."
      />
    </>
  );
}
