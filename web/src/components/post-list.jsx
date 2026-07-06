import { useCallback, useEffect, useState } from "react";

import PostCard from "./post-card.jsx";

export default function PostList({ fetchPage, emptyText = "Nothing here yet." }) {
  const [items, setItems] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(
    async (after) => {
      setLoading(true);
      setError(null);
      try {
        const page = await fetchPage(after);
        setItems((prev) => (after ? [...prev, ...page.items] : page.items));
        setCursor(page.next_cursor);
        setHasMore(page.next_cursor !== null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [fetchPage],
  );

  useEffect(() => {
    load(null);
  }, [load]);

  const onDeleted = (id) => setItems((prev) => prev.filter((p) => p.id !== id));

  if (error) return <p className="state-msg">{error}</p>;
  if (!loading && items.length === 0)
    return <p className="state-msg">{emptyText}</p>;

  return (
    <div className="post-list">
      {items.map((post) => (
        <PostCard key={post.id} post={post} onDeleted={onDeleted} />
      ))}
      {loading && <p className="state-msg">Loading…</p>}
      {hasMore && !loading && (
        <button className="btn ghost block" onClick={() => load(cursor)}>
          Load more
        </button>
      )}
    </div>
  );
}
