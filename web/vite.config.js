import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In dev, proxy /api to the compose-exposed services so `npm run dev`
// works against a running backend without CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api/users": "http://localhost:9001",
      "/api/posts": "http://localhost:9002",
      "/api/timeline": "http://localhost:9003",
      "/api/search": "http://localhost:9003",
    },
  },
});
