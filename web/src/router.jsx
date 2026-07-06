import { useEffect, useState } from "react";

function currentPath() {
  return window.location.hash.slice(1) || "/";
}

export function useRoute() {
  const [path, setPath] = useState(currentPath);
  useEffect(() => {
    const onChange = () => setPath(currentPath());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return { path, parts: path.split("/").filter(Boolean) };
}

export function navigate(to) {
  window.location.hash = to;
}

export function Link({ to, className, children, onClick }) {
  return (
    <a href={`#${to}`} className={className} onClick={onClick}>
      {children}
    </a>
  );
}
