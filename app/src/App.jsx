import React, { useState } from "react";
import "./App.css";

function App() {
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState("youtube");
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setDownloadUrl("");
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/clip?url=${encodeURIComponent(
          url
        )}&start=00:00:00&end=00:00:30&platform=${platform}`,
        { method: "POST" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error generating clip");
      }

      setDownloadUrl(`http://localhost:8000/download/${data.job_id}`);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div className="layout" style={{ display: "flex", minHeight: "100vh" }}>
      <aside
        className="sidebar"
        style={{
          flexShrink: 0,
          width: 220,
          backgroundColor: "#1e293b",
          color: "white",
          padding: "2rem 1rem",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <h2 style={{ marginBottom: "2rem" }}>AI Clipper</h2>
        <nav
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
            fontWeight: "500",
          }}
        >
          <a href="#" style={{ color: "inherit", textDecoration: "none" }}>
            Dashboard
          </a>
          <a href="#" style={{ color: "inherit", textDecoration: "none" }}>
            My Clips
          </a>
          <a href="#" style={{ color: "inherit", textDecoration: "none" }}>
            Analytics
          </a>
          <a href="#" style={{ color: "inherit", textDecoration: "none" }}>
            Settings
          </a>
        </nav>
      </aside>

      <main
        className="main"
        style={{
          flexGrow: 1,
          padding: "3rem 4rem",
          backgroundColor: "#f9fafb",
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
        }}
      >
        <div
          className="card"
          style={{
            backgroundColor: "white",
            padding: "2rem 2.5rem",
            borderRadius: 8,
            boxShadow:
              "0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)",
            maxWidth: 480,
            width: "100%",
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
          }}
        >
          <h1 style={{ marginBottom: 0, fontSize: "1.8rem" }}>Generate AI Clip</h1>
          <p style={{ marginTop: 0, color: "#6b7280" }}>
            Auto-create 30 second clips optimized for your platform.
          </p>

          <form
            onSubmit={handleSubmit}
            style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}
          >
            <label
              htmlFor="url-input"
              style={{ fontWeight: "600", fontSize: "0.9rem", color: "#374151" }}
            >
              Video URL
            </label>
            <input
              id="url-input"
              type="url"
              placeholder="Paste YouTube URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              style={{
                padding: "0.5rem 0.75rem",
                fontSize: "1rem",
                borderRadius: 6,
                border: "1px solid #d1d5db",
                outlineOffset: 2,
                outlineColor: "#2563eb",
              }}
              aria-describedby="urlHelp"
            />
            <small id="urlHelp" style={{ color: "#6b7280" }}>
              Please enter a valid URL to generate your clip.
            </small>

            <label
              htmlFor="platform-select"
              style={{ fontWeight: "600", fontSize: "0.9rem", color: "#374151" }}
            >
              Select Platform
            </label>
            <select
              id="platform-select"
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              style={{
                padding: "0.5rem 0.75rem",
                fontSize: "1rem",
                borderRadius: 6,
                border: "1px solid #d1d5db",
                backgroundColor: "white",
                cursor: "pointer",
              }}
              aria-label="Platform selection"
            >
              <option value="youtube">YouTube (16:9)</option>
              <option value="tiktok">TikTok (9:16)</option>
              <option value="instagram">Instagram (1:1)</option>
            </select>

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: "1rem",
                padding: "0.75rem",
                backgroundColor: loading ? "#93c5fd" : "#3b82f6",
                color: "white",
                fontWeight: "600",
                border: "none",
                borderRadius: 6,
                cursor: loading ? "not-allowed" : "pointer",
                transition: "background-color 0.3s ease",
              }}
              aria-busy={loading}
            >
              {loading ? "Generating..." : "Generate Clip"}
            </button>
          </form>

          {error && (
            <div
              role="alert"
              style={{
                marginTop: "1rem",
                padding: "0.75rem 1rem",
                backgroundColor: "#fee2e2",
                color: "#b91c1c",
                borderRadius: 6,
                fontWeight: "600",
              }}
            >
              {error}
            </div>
          )}

          {downloadUrl && (
            <a
              className="download"
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                marginTop: "1.5rem",
                fontWeight: "600",
                color: "#2563eb",
                textDecoration: "underline",
                display: "inline-block",
              }}
            >
              Download Your Clip
            </a>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;