import { useCallback, useEffect, useState } from "react";

import { api } from "../api.js";
import { useAuth } from "../auth-context.jsx";
import Avatar from "../components/avatar.jsx";
import PostList from "../components/post-list.jsx";
import { navigate } from "../router.jsx";

export default function Profile({ username }) {
  const { me } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setProfile(null);
    api.profile(username).then(setProfile).catch((err) => setError(err.message));
  }, [username]);

  const fetchPage = useCallback(
    (cursor) => api.userTimeline(username, cursor),
    [username],
  );

  const toggleFollow = async () => {
    if (!me) return navigate("/auth");
    const followed = profile.followed_by_me;
    setProfile({
      ...profile,
      followed_by_me: !followed,
      followers: profile.followers + (followed ? -1 : 1),
    });
    try {
      await (followed ? api.unfollow(username) : api.follow(username));
    } catch {
      setProfile(profile);
    }
  };

  if (error) return <p className="state-msg">{error}</p>;
  if (!profile) return <p className="state-msg">Loading…</p>;

  const isMe = me && me.id === profile.id;

  return (
    <>
      <header className="profile-header">
        <Avatar username={profile.username} size={72} />
        <div className="profile-info">
          <h2>{profile.display_name}</h2>
          <p className="post-meta">@{profile.username}</p>
          {profile.bio && <p className="profile-bio">{profile.bio}</p>}
          <p className="profile-stats">
            <strong>{profile.following}</strong> following ·{" "}
            <strong>{profile.followers}</strong> followers
          </p>
        </div>
        {!isMe && (
          <button
            className={`btn ${profile.followed_by_me ? "ghost" : "primary"}`}
            onClick={toggleFollow}
          >
            {profile.followed_by_me ? "Following ✓" : "Follow"}
          </button>
        )}
      </header>
      <PostList fetchPage={fetchPage} emptyText="No posts yet." />
    </>
  );
}
