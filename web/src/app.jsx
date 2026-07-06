import { AuthProvider, useAuth } from "./auth-context.jsx";
import Layout from "./components/layout.jsx";
import Feed from "./pages/feed.jsx";
import Landing from "./pages/landing.jsx";
import Profile from "./pages/profile.jsx";
import Search from "./pages/search.jsx";
import Thread from "./pages/thread.jsx";
import { useRoute } from "./router.jsx";

function Routes({ parts }) {
  if (parts.length === 0) return <Feed />;
  if (parts[0] === "search") return <Search />;
  if (parts[0] === "u" && parts[1]) return <Profile username={parts[1]} />;
  if (parts[0] === "p" && parts[1]) return <Thread postId={parts[1]} />;
  return <p className="state-msg">Page not found.</p>;
}

function Shell() {
  const { me, loading } = useAuth();
  const { parts } = useRoute();

  if (loading) return <p className="state-msg">Loading…</p>;

  // Logged out: home and /auth are one full-screen landing — sign-in
  // happens right there, no extra click, no app chrome.
  if (!me && (parts.length === 0 || parts[0] === "auth")) return <Landing />;

  return (
    <Layout>
      <Routes parts={parts} />
    </Layout>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}
