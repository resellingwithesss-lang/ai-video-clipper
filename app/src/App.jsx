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

    if (!url.trim()) {
      setError("YouTube URL cannot be empty.");
      return;
    }

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
        margin: "64px auto",
        padding: "32px 32px 40px",
        borderRadius: "12px",
        boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        backgroundColor: "#fff",
        display: "flex",
        flexDirection: "column",
        gap: "32px"
      }}
      aria-live="polite"
    >
      <h1 style={{ textAlign: "center", marginBottom: "26px", color: "#222", fontWeight: "700", fontSize: "1.8rem" }}>
        AI Video Clipper (Local)
      </h1>

      <form onSubmit={handleSubmit} noValidate aria-describedby="formError" style={{ display: "flex", flexDirection: "column", gap: "28px" }}>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <label
            htmlFor="urlInput"
            style={{ marginBottom: "8px", fontWeight: "600", color: "#333", userSelect: "none" }}
          >
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
              padding: "12px 16px",
              borderRadius: "6px",
              border: `1.5px solid ${error.includes("URL") || error === "YouTube URL cannot be empty." ? "#d93025" : "#ccc"}`,
              fontSize: "15px",
              transition: "border-color 0.3s",
              boxSizing: "border-box"
            }}
            aria-describedby="urlHelp"
            aria-invalid={error.includes("URL") || error === "YouTube URL cannot be empty." ? "true" : undefined}
          />
          <small id="urlHelp" style={{ marginTop: "6px", color: "#666", fontSize: "13px", lineHeight: "1.3" }}>
            Enter the full YouTube URL you want to clip.
          </small>
        </div>

        <div style={{ display: "flex", gap: "24px", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 45%", minWidth: "160px", display: "flex", flexDirection: "column" }}>
            <label
              htmlFor="startInput"
              style={{ marginBottom: "8px", fontWeight: "600", color: "#333", userSelect: "none" }}
            >
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
                padding: "12px 16px",
                borderRadius: "6px",
                border: `1.5px solid ${error.includes("Start Time") ? "#d93025" : "#ccc"}`,
                fontSize: "15px",
                transition: "border-color 0.3s",
                boxSizing: "border-box"
              }}
              aria-invalid={error.includes("Start Time") ? "true" : undefined}
            />
          </div>

          <div style={{ flex: "1 1 45%", minWidth: "160px", display: "flex", flexDirection: "column" }}>
            <label
              htmlFor="endInput"
              style={{ marginBottom: "8px", fontWeight: "600", color: "#333", userSelect: "none" }}
            >
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
                padding: "12px 16px",
                borderRadius: "6px",
                border: `1.5px solid ${error.includes("End Time") ? "#d93025" : "#ccc"}`,
                fontSize: "15px",
                transition: "border-color 0.3s",
                boxSizing: "border-box"
              }}
              aria-invalid={error.includes("End Time") ? "true" : undefined}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "14px 0",
            backgroundColor: loading ? "#0056b3" : "#007bff",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "wait" : "pointer",
            fontSize: "17px",
            fontWeight: "600",
            boxShadow: loading ? "none" : "0 4px 10px rgba(0,123,255,0.3)",
            transition: "background-color 0.3s, box-shadow 0.3s",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "10px",
            userSelect: "none",
            WebkitTapHighlightColor: "transparent"
          }}
          aria-busy={loading}
          aria-label={loading ? "Generating clip" : "Generate clip"}
        >
          {loading && (
            <svg
              aria-hidden="true"
              focusable="false"
              width="20"
              height="20"
              viewBox="0 0 50 50"
              style={{ animation: "spin 1s linear infinite" }}
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                cx="25"
                cy="25"
                r="20"
                fill="none"
                stroke="#fff"
                strokeWidth="5"
                strokeLinecap="round"
                strokeDasharray="31.415, 31.415"
                transform="rotate(0 25 25)"
              />
            </svg>
          )}
          {loading ? "Generating your clip..." : "Generate Clip"}
        </button>
      </form>

      {error && (
        <p
          role="alert"
          id="formError"
          style={{
            color: "#d93025",
            marginTop: "4px",
            fontWeight: "600",
            backgroundColor: "#fce8e6",
            padding: "14px 20px",
            borderRadius: "6px",
            border: "1px solid #d93025",
            lineHeight: "1.4",
            fontSize: "14px",
            userSelect: "text",
            wordBreak: "break-word"
          }}
        >
          {error}
        </p>
      )}

      {downloadUrl && (
        <div
          style={{
            marginTop: "20px",
            backgroundColor: "#d7f0ff",
            borderRadius: "8px",
            padding: "18px 24px",
            textAlign: "center",
            border: "1px solid #a1d4fb",
            fontSize: "16px",
            fontWeight: "600",
            userSelect: "text",
            boxShadow: "0 2px 8px rgba(0,123,255,0.15)",
            transition: "background-color 0.3s"
          }}
        >
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              color: "#007bff",
              fontWeight: "700",
              textDecoration: "underline",
              outlineOffset: "2px",
              wordBreak: "break-word"
            }}
            aria-label="Download your clipped video"
          >
            Download Your Clip
          </a>
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% {transform: rotate(0deg);}
          100% {transform: rotate(360deg);}
        }
        input:focus, button:focus {
          outline: 2px solid #007bff;
          outline-offset: 2px;
        }
        button:disabled {
          opacity: 0.7;
        }
      `}</style>
    </div>
  );
}

export default App;