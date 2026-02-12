import React, { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");

  const validateTime = (time) => {
    // Simple HH:MM:SS format check
    return /^\d{2}:\d{2}:\d{2}$/.test(time);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setDownloadUrl("");

    if (!validateTime(start)) {
      setError("Start Time must be in HH:MM:SS format.");
      return;
    }
    if (!validateTime(end)) {
      setError("End Time must be in HH:MM:SS format.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/clip?url=${encodeURIComponent(url)}&start=${start}&end=${end}`,
        { method: "POST" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error generating clip");
      }

      setDownloadUrl(
        `http://localhost:8000/download/${data.job_id}`
      );

    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        maxWidth: "480px",
        margin: "60px auto",
        padding: "32px 28px",
        borderRadius: "12px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        backgroundColor: "#fff",
      }}
      aria-live="polite"
    >
      <h1 style={{ textAlign: "center", marginBottom: "30px", color: "#222" }}>AI Video Clipper (Local)</h1>

      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="urlInput" style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333" }}>
          YouTube URL
        </label>
        <input
          id="urlInput"
          type="url"
          placeholder="Paste YouTube URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          autoComplete="off"
          style={{
            width: "100%",
            padding: "10px 12px",
            marginBottom: "22px",
            borderRadius: "6px",
            border: "1.5px solid #ccc",
            fontSize: "15px",
            transition: "border-color 0.3s",
          }}
          aria-describedby="urlHelp"
          aria-invalid={error.includes("URL") ? "true" : "false"}
        />
        <small id="urlHelp" style={{ display: "block", marginBottom: "18px", color: "#666" }}>
          Enter the full YouTube URL you want to clip.
        </small>

        <label htmlFor="startInput" style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333" }}>
          Start Time (HH:MM:SS)
        </label>
        <input
          id="startInput"
          type="text"
          placeholder="00:00:00"
          value={start}
          onChange={(e) => setStart(e.target.value)}
          required
          autoComplete="off"
          inputMode="numeric"
          style={{
            width: "100%",
            padding: "10px 12px",
            marginBottom: "20px",
            borderRadius: "6px",
            border: "1.5px solid #ccc",
            fontSize: "15px",
            transition: "border-color 0.3s",
          }}
          aria-invalid={error.includes("Start Time") ? "true" : "false"}
        />

        <label htmlFor="endInput" style={{ display: "block", marginBottom: "6px", fontWeight: "600", color: "#333" }}>
          End Time (HH:MM:SS)
        </label>
        <input
          id="endInput"
          type="text"
          placeholder="00:00:00"
          value={end}
          onChange={(e) => setEnd(e.target.value)}
          required
          autoComplete="off"
          inputMode="numeric"
          style={{
            width: "100%",
            padding: "10px 12px",
            marginBottom: "28px",
            borderRadius: "6px",
            border: "1.5px solid #ccc",
            fontSize: "15px",
            transition: "border-color 0.3s",
          }}
          aria-invalid={error.includes("End Time") ? "true" : "false"}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "14px",
            backgroundColor: loading ? "#0056b3" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "progress" : "pointer",
            fontSize: "17px",
            fontWeight: "600",
            boxShadow: loading ? "none" : "0 4px 10px rgba(0,123,255,0.3)",
            transition: "background-color 0.3s, box-shadow 0.3s",
          }}
          aria-busy={loading}
        >
          {loading ? "Generating your clip..." : "Generate Clip"}
        </button>
      </form>

      {error && (
        <p
          role="alert"
          style={{
            color: "#d93025",
            marginTop: "22px",
            fontWeight: "600",
            backgroundColor: "#fce8e6",
            padding: "12px 16px",
            borderRadius: "6px",
            border: "1px solid #d93025",
          }}
        >
          {error}
        </p>
      )}

      {downloadUrl && (
        <div
          style={{
            marginTop: "30px",
            backgroundColor: "#d7f0ff",
            borderRadius: "8px",
            padding: "14px 20px",
            textAlign: "center",
            border: "1px solid #a1d4fb",
          }}
        >
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#007bff", fontWeight: "700", fontSize: "16px", textDecoration: "underline" }}
            aria-label="Download your clipped video"
          >
            Download Your Clip
          </a>
        </div>
      )}
    </div>
  );
}

export default App;