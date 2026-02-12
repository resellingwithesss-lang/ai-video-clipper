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
    if (!email.trim()) {
      alert("Please enter your email");
      return;
    }
    try {
      setLoading(true);

      await axios.post(
        `${API}/login`,
        { email: email },
        {
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      setLoggedIn(true);
      setLoading(false);
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Login failed. Please check your email and try again.");
      setLoading(false);
    }
  };

  // GENERATE CLIP
  const generateClip = async () => {
    if (!url.trim()) {
      alert("Please enter a YouTube URL");
      return;
    }
    try {
      setLoading(true);

      const res = await axios.post(
        `${API}/clip`,
        null,
        {
          params: {
            url: url,
            start: "0",
            end: "10"
          }
        }
      );

      window.open(res.data.download_url, "_blank");
      setLoading(false);
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Error generating clip. Please verify the URL and try again.");
      setLoading(false);
    }
  };

  const commonInputStyle = {
    width: 360,
    padding: 14,
    fontSize: 16,
    borderRadius: 6,
    border: "1px solid #ccc",
    boxSizing: "border-box"
  };

  const containerStyle = {
    maxWidth: 480,
    margin: "120px auto",
    textAlign: "center",
    padding: 24,
    boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
    borderRadius: 8,
    backgroundColor: "#fff"
  };

  const buttonStyle = {
    width: 180,
    padding: "12px 0",
    fontSize: 16,
    borderRadius: 6,
    border: "none",
    cursor: loading ? "default" : "pointer",
    backgroundColor: loading ? "#999" : "#007bff",
    color: "white",
    fontWeight: "600",
    transition: "background-color 0.3s ease"
  };

  // LOGIN SCREEN
  if (!loggedIn) {
    return (
      <div style={containerStyle}>
        <h1 style={{ marginBottom: 24 }}>Login</h1>

        <input
          type="email"
          style={commonInputStyle}
          placeholder="Enter email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          disabled={loading}
          onKeyDown={(e) => e.key === 'Enter' && !loading && login()}
          aria-label="Email address"
        />

        <div style={{ height: 20 }}></div>

        <button onClick={login} disabled={loading || !email.trim()} style={buttonStyle}>
          {loading ? "Loading..." : "Enter"}
        </button>
      </div>
    );
  }

  // MAIN APP
  return (
    <div style={containerStyle}>
      <h1 style={{ marginBottom: 24 }}>AI Video Clipper</h1>

      <input
        type="url"
        style={commonInputStyle}
        placeholder="Paste YouTube URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={loading}
        onKeyDown={(e) => e.key === 'Enter' && !loading && generateClip()}
        aria-label="YouTube URL"
      />

      <div style={{ height: 20 }}></div>

      <button onClick={generateClip} disabled={loading || !url.trim()} style={buttonStyle}>
        {loading ? "Generating..." : "Generate Clip"}
      </button>
    </div>
  );
}