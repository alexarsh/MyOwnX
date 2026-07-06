import { useAuth } from "../auth-context.jsx";
import { Link, navigate, useRoute } from "../router.jsx";
import Avatar from "./avatar.jsx";

const NAV = [
  { to: "/", label: "Home", icon: "◆" },
  { to: "/search", label: "Search", icon: "◎" },
];

export default function Layout({ children }) {
  const { me, signOut } = useAuth();
  const { path } = useRoute();

  return (
    <div className="layout">
      <aside className="sidebar">
        <Link to="/" className="brand">
          MyOwn<span className="brand-x">X</span>
        </Link>
        <nav>
          {NAV.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`nav-link ${path === item.to ? "active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
          {me && (
            <Link
              to={`/u/${me.username}`}
              className={`nav-link ${path === `/u/${me.username}` ? "active" : ""}`}
            >
              <span className="nav-icon">◉</span>
              <span className="nav-label">Profile</span>
            </Link>
          )}
          {!me && (
            <Link to="/auth" className="btn primary block join-btn">
              Join in
            </Link>
          )}
        </nav>
        {me && (
          <div className="sidebar-footer">
            <Link to={`/u/${me.username}`} className="me-chip">
              <Avatar username={me.username} size={34} />
              <span className="me-name">@{me.username}</span>
            </Link>
            <button
              className="btn ghost"
              onClick={() => {
                signOut();
                navigate("/");
              }}
            >
              Sign out
            </button>
          </div>
        )}
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
