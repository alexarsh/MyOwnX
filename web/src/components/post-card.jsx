import { useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth-context.jsx";
import { Link, navigate } from "../router.jsx";
import Avatar from "./avatar.jsx";

function timeAgo(iso) {
  const seconds = Math.max(1, (Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return `${Math.floor(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
  return `${Math.floor(seconds / 86400)}d`;
}

function replyLabel(count) {
  if (count === 0) return "Reply";
  return count === 1 ? "1 reply" : `${count} replies`;
}

export default function PostCard({ post, onDeleted, linkToThread = true }) {
  const { me } = useAuth();
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likes, setLikes] = useState(post.like_count);
  const author = post.author || { username: "unknown", display_name: "Unknown" };
  const mine = me && me.id === post.author_id;
  const stop = (event) => event.stopPropagation();

  const openThread = () => {
    if (linkToThread) navigate(`/p/${post.id}`);
  };

  const toggleLike = async (event) => {
    event.stopPropagation();
    if (!me) return navigate("/auth");
    setLiked(!liked);
    setLikes(likes + (liked ? -1 : 1));
    try {
      await (liked ? api.unlike(post.id) : api.like(post.id));
    } catch {
      setLiked(liked);
      setLikes(likes);
    }
  };

  const remove = async (event) => {
    event.stopPropagation();
    if (!window.confirm("Delete this post?")) return;
    await api.deletePost(post.id);
    onDeleted?.(post.id);
  };

  return (
    <article
      className={`post-card ${linkToThread ? "clickable" : ""}`}
      onClick={openThread}
    >
      <Link to={`/u/${author.username}`} onClick={stop}>
        <Avatar username={author.username} />
      </Link>
      <div className="post-body">
        <header className="post-header">
          <Link to={`/u/${author.username}`} className="post-author" onClick={stop}>
            {author.display_name}
          </Link>
          <span className="post-meta">
            @{author.username} · {timeAgo(post.created_at)}
          </span>
        </header>
        <p className="post-text">{post.text}</p>
        <footer className="post-actions">
          {linkToThread && (
            <span className="action">◌ {replyLabel(post.reply_count)}</span>
          )}
          <button
            className={`action like ${liked ? "liked" : ""}`}
            onClick={toggleLike}
          >
            {liked ? "♥" : "♡"} {likes}
          </button>
          {mine && (
            <button className="action danger" onClick={remove}>
              ✕
            </button>
          )}
        </footer>
      </div>
    </article>
  );
}
