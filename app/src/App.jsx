import React, { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setDownloadUrl("");
    setLoading(true);

    try {
      const response = await fetch(
        `https://ai-clipper-backend.onrender.com/clip?url=${encodeURIComponent(
          url
        )}&start=${start}&end=${end}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error generating clip");
      }

      setDownloadUrl(
        `https://ai-clipper-backend.onrender.com/download/${data.job_id}`
      );
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        maxWidth: "500px",
        margin: "50px auto",
        padding: "30px",
        borderRadius: "12px",
        boxShadow: "0 8px 20px rgba(0,0,0,0.1)",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1 style={{ textAlign: "center" }}>AI Video Clipper</h1>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Paste YouTube URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            marginBottom: "15px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />

        <input
          type="text"
          placeholder="Start Time (HH:MM:SS)"
          value={start}
          onChange={(e) => setStart(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            marginBottom: "5px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />
        <p style={{ fontSize: "12px", color: "#666" }}>
          Format: HH:MM:SS (example: 00:00:10)
        </p>

        <input
          type="text"
          placeholder="End Time (HH:MM:SS)"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
          required
          style={{
            width: "100%",
            padding: "10px",
            marginBottom: "5px",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />
        <p style={{ fontSize: "12px", color: "#666" }}>
          Format: HH:MM:SS (example: 00:01:00)
        </p>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "15px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          {loading ? "Generating..." : "Generate Clip"}
        </button>
      </form>

      {error && (
        <p style={{ color: "red", marginTop: "15px" }}>
          {error}
        </p>
      )}

      {downloadUrl && (
        <div style={{ marginTop: "20px" }}>
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#007bff", fontWeight: "bold" }}
          >
            Download Your Clip
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
