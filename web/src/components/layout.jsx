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

  // Logged-out visitors on deep links (profiles, threads, search) get a
  // slim top bar with a single way in — the app shell is for members.
  if (!me) {
    return (
      <div className="solo-layout">
        <header className="topbar">
          <Link to="/" className="brand">
            MyOwn<span className="brand-x">X</span>
          </Link>
          <Link to="/auth" className="btn primary">
            Sign in
          </Link>
        </header>
        <main className="content solo-content">{children}</main>
      </div>
    );
  }

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
          <Link
            to={`/u/${me.username}`}
            className={`nav-link ${path === `/u/${me.username}` ? "active" : ""}`}
          >
            <span className="nav-icon">◉</span>
            <span className="nav-label">Profile</span>
          </Link>
        </nav>
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
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}
