import { AuthProvider } from "./auth-context.jsx";
import Layout from "./components/layout.jsx";
import Auth from "./pages/auth.jsx";
import Feed from "./pages/feed.jsx";
import Profile from "./pages/profile.jsx";
import Search from "./pages/search.jsx";
import Thread from "./pages/thread.jsx";
import { useRoute } from "./router.jsx";

function Routes() {
  const { parts } = useRoute();

  if (parts.length === 0) return <Feed />;
  if (parts[0] === "auth") return <Auth />;
  if (parts[0] === "search") return <Search />;
  if (parts[0] === "u" && parts[1]) return <Profile username={parts[1]} />;
  if (parts[0] === "p" && parts[1]) return <Thread postId={parts[1]} />;
  return <p className="state-msg">Page not found.</p>;
}

export default function App() {
  return (
    <AuthProvider>
      <Layout>
        <Routes />
      </Layout>
    </AuthProvider>
  );
}
