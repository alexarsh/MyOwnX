import { useCallback, useState } from "react";

import { api } from "../api.js";
import Composer from "../components/composer.jsx";
import PostList from "../components/post-list.jsx";

export default function Feed() {
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchPage = useCallback((cursor) => api.timeline(cursor), []);

  return (
    <>
      <h2 className="page-title">Home</h2>
      <Composer onPosted={() => setRefreshKey((k) => k + 1)} />
      <PostList
        key={refreshKey}
        fetchPage={fetchPage}
        emptyText="Your feed is empty — follow people or write your first post."
      />
    </>
  );
}
