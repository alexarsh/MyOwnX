import { useCallback, useEffect, useState } from "react";

import { api } from "../api.js";
import Composer from "../components/composer.jsx";
import PostCard from "../components/post-card.jsx";
import { navigate } from "../router.jsx";

export default function Thread({ postId }) {
  const [thread, setThread] = useState(null);
  const [error, setError] = useState(null);

  const load = useCallback(() => {
    api.thread(postId).then(setThread).catch((err) => setError(err.message));
  }, [postId]);

  useEffect(load, [load]);

  const goBack = () => {
    if (window.history.length > 1) window.history.back();
    else navigate("/");
  };

  if (error) return <p className="state-msg">{error}</p>;
  if (!thread) return <p className="state-msg">Loading…</p>;

  return (
    <>
      <header className="page-header">
        <button className="back-btn" onClick={goBack} aria-label="Go back">
          ←
        </button>
        <h2 className="page-title">Thread</h2>
      </header>
      <PostCard
        post={thread.post}
        linkToThread={false}
        onDeleted={() => navigate("/")}
      />
      <Composer
        replyTo={thread.post.id}
        onPosted={load}
        placeholder="Post your reply"
      />
      <div className="thread-replies">
        {thread.replies.map((reply) => (
          <PostCard
            key={reply.id}
            post={reply}
            linkToThread={false}
            onDeleted={load}
          />
        ))}
      </div>
    </>
  );
}
