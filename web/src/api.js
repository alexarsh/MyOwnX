const TOKEN_KEY = "myownx_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const headers = {};
  if (options.body) headers["content-type"] = "application/json";
  const token = getToken();
  if (token) headers.authorization = `Bearer ${token}`;
  const response = await fetch(`/api${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : null;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return data;
}

export const api = {
  signup: (body) => request("/users/signup", { method: "POST", body }),
  login: (body) => request("/users/login", { method: "POST", body }),
  me: () => request("/users/me"),
  profile: (username) => request(`/users/${username}`),
  follow: (username) => request(`/users/${username}/follow`, { method: "POST" }),
  unfollow: (username) => request(`/users/${username}/follow`, { method: "DELETE" }),
  timeline: (cursor) => request(`/timeline${cursor ? `?cursor=${cursor}` : ""}`),
  userTimeline: (username, cursor) =>
    request(`/timeline/user/${username}${cursor ? `?cursor=${cursor}` : ""}`),
  createPost: (body) => request("/posts", { method: "POST", body }),
  deletePost: (id) => request(`/posts/${id}`, { method: "DELETE" }),
  thread: (id) => request(`/posts/${id}`),
  like: (id) => request(`/posts/${id}/like`, { method: "POST" }),
  unlike: (id) => request(`/posts/${id}/like`, { method: "DELETE" }),
  search: (q, type) =>
    request(`/search?q=${encodeURIComponent(q)}&type=${type}`),
};
