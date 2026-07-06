import AuthPanel from "../components/auth-panel.jsx";

// Full-screen logged-out landing: brand statement left, sign-in right.
export default function Landing() {
  return (
    <div className="landing">
      <aside className="landing-side" aria-hidden="true">
        <span className="landing-glyph">X</span>
      </aside>
      <main className="landing-main">
        <p className="brand landing-brand">
          MyOwn<span className="brand-x">X</span>
        </p>
        <h1 className="landing-title">
          Say it <em>loud.</em>
        </h1>
        <p className="landing-sub">
          Post in 280 characters. Follow interesting people. Own your feed.
        </p>
        <AuthPanel />
      </main>
    </div>
  );
}
