import axios from "axios";
import { useState } from "react";

const API = "https://ai-clipper-backend.onrender.com";

export default function App() {
  const [email, setEmail] = useState("");
  const [url, setUrl] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);

  // LOGIN
  const login = async () => {
    try {
      setLoading(true);

      await axios.post(`${API}/login`, {
        email: email
      });

      setLoggedIn(true);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Login failed");
      setLoading(false);
    }
  };

  // GENERATE CLIP
  const generateClip = async () => {
    try {
      setLoading(true);

      const res = await axios.post(`${API}/clip`, null, {
        params: {
          url: url,
          start: "0",
          end: "10"
        }
      });

      window.open(res.data.download_url, "_blank");
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Error generating clip");
      setLoading(false);
    }
  };

  // LOGIN SCREEN
  if (!loggedIn) {
    return (
      <div style={{ textAlign: "center", marginTop: "150px" }}>
        <h1>Login</h1>

        <input
          style={{ width: 300, padding: 10 }}
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <br /><br />

        <button onClick={login} disabled={loading}>
          {loading ? "Loading..." : "Enter"}
        </button>
      </div>
    );
  }

  // MAIN APP
  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>AI Video Clipper</h1>

      <input
        style={{ width: 400, padding: 10 }}
        placeholder="Paste YouTube URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <br /><br />

      <button onClick={generateClip} disabled={loading}>
        {loading ? "Generating..." : "Generate Clip"}
      </button>
    </div>
  );
}
