import { createContext, useContext, useEffect, useState } from "react";

import { api, getToken, setToken } from "./api.js";

const AuthContext = createContext({ me: null, loading: false });

export function AuthProvider({ children }) {
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  useEffect(() => {
    if (!getToken()) return;
    api
      .me()
      .then(setMe)
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  const signIn = async (token) => {
    setToken(token);
    setMe(await api.me());
  };

  const signOut = () => {
    setToken(null);
    setMe(null);
  };

  return (
    <AuthContext.Provider value={{ me, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
