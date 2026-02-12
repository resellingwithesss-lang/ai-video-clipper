import React, { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [start, setStart] = useState("00:00:00");
  const [end, setEnd] = useState("00:00:30");
  const [quality, setQuality] = useState("1080p");
  const [style, setStyle] = useState("Standard");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const validYouTubeUrl = (value) =>
    /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)\S+/.test(value.trim());

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validYouTubeUrl(url.trim())) {
      setMessage("⚠️ Please enter a valid YouTube URL.");
      return;
    }
    setLoading(true);
    setMessage("Processing clip with AI...");

    try {
      const response = await fetch(
        `http://localhost:8000/clip?url=${encodeURIComponent(
          url
        )}&start=${start}&end=${end}`,
        { method: "POST" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Error generating clip");
      }

      setMessage("🎉 Clip successfully generated!");
      window.open(`http://localhost:8000/download/${data.job_id}`, "_blank", "noopener,noreferrer");
    } catch (err) {
      setMessage("⚠️ Error: " + err.message);
    }

    setLoading(false);
  };

  return (
    <div style={styles.page}>
      <nav style={styles.sidebar} aria-label="Primary navigation">
        <h2 style={styles.sidebarHeader}>🎬 Creator AI</h2>
        <ul style={styles.navList}>
          {["Dashboard", "My Clips", "Analytics", "AI Tools"].map((item) => (
            <li
              key={item}
              style={styles.navItem}
              tabIndex={0}
              role="link"
              aria-label={item}
              onKeyDown={(e) => e.key === "Enter" && e.currentTarget.click()}
              onMouseOver={(e) =>
                (e.currentTarget.style.backgroundColor = "#1f2937")
              }
              onFocus={(e) =>
                (e.currentTarget.style.backgroundColor = "#1f2937")
              }
              onMouseOut={(e) =>
                (e.currentTarget.style.backgroundColor = "transparent")
              }
              onBlur={(e) =>
                (e.currentTarget.style.backgroundColor = "transparent")
              }
            >
              {item}
            </li>
          ))}
        </ul>
      </nav>

      <main style={styles.main}>
        <div style={styles.container}>
          <h1 style={{ marginBottom: 32, fontWeight: "700" }}>
            AI Clip Generator Studio
          </h1>

          <form
            onSubmit={handleSubmit}
            style={styles.card}
            aria-live="polite"
            aria-busy={loading}
            noValidate
            autoComplete="off"
          >
            <label htmlFor="urlInput" style={styles.label}>
              YouTube URL
            </label>
            <input
              id="urlInput"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Paste YouTube link"
              required
              style={{
                ...styles.input,
                borderColor:
                  url && !validYouTubeUrl(url)
                    ? "#dc2626"
                    : "#cbd5e1",
              }}
              aria-describedby="urlHelp"
              disabled={loading}
              autoComplete="off"
              autoFocus
              aria-invalid={url && !validYouTubeUrl(url)}
              aria-required="true"
            />
            <small
              id="urlHelp"
              style={{
                ...styles.helpText,
                color:
                  url && !validYouTubeUrl(url)
                    ? "#dc2626"
                    : "#6b7280",
              }}
            >
              Enter a valid YouTube video URL
            </small>

            <div style={styles.timeInputsWrapper}>
              <div style={styles.timeInputContainer}>
                <label htmlFor="startTime" style={styles.label}>
                  Start Time
                </label>
                <input
                  id="startTime"
                  type="time"
                  step="1"
                  value={start}
                  onChange={(e) => {
                    const val = e.target.value;
                    if(val <= end) setStart(val);
                  }}
                  style={styles.input}
                  max={end}
                  aria-describedby="startHelp"
                  disabled={loading}
                  pattern="\d{2}:\d{2}:\d{2}"
                  aria-label="Clip start time in hh:mm:ss format"
                />
                <small id="startHelp" style={styles.helpText}>
                  Clip start time (hh:mm:ss)
                </small>
              </div>

              <div style={styles.timeInputContainer}>
                <label htmlFor="endTime" style={styles.label}>
                  End Time
                </label>
                <input
                  id="endTime"
                  type="time"
                  step="1"
                  value={end}
                  onChange={(e) => {
                    const val = e.target.value;
                    if(val >= start) setEnd(val);
                  }}
                  style={styles.input}
                  min={start}
                  aria-describedby="endHelp"
                  disabled={loading}
                  pattern="\d{2}:\d{2}:\d{2}"
                  aria-label="Clip end time in hh:mm:ss format"
                />
                <small id="endHelp" style={styles.helpText}>
                  Clip end time (hh:mm:ss)
                </small>
              </div>
            </div>

            <label htmlFor="quality" style={styles.label}>
              Output Quality
            </label>
            <select
              id="quality"
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              style={styles.input}
              disabled={loading}
              aria-label="Select output quality"
            >
              <option value="1080p">1080p</option>
              <option value="720p">720p</option>
              <option value="4K">4K</option>
            </select>

            <label htmlFor="style" style={styles.label}>
              AI Enhancement Style
            </label>
            <select
              id="style"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              style={styles.input}
              disabled={loading}
              aria-label="Select AI enhancement style"
            >
              <option value="Standard">Standard</option>
              <option value="Viral Optimized">Viral Optimized</option>
              <option value="Shorts Format">Shorts Format</option>
              <option value="Podcast Cut">Podcast Cut</option>
            </select>

            <button
              type="submit"
              disabled={
                loading || !url.trim() || !validYouTubeUrl(url)
              }
              style={{
                ...styles.button,
                opacity: loading || !url.trim() || !validYouTubeUrl(url) ? 0.7 : 1,
                cursor:
                  loading || !url.trim() || !validYouTubeUrl(url)
                    ? "not-allowed"
                    : "pointer",
              }}
              aria-live="polite"
              aria-label={loading ? "Processing AI clip" : "Generate AI Clip"}
            >
              {loading ? (
                <span>
                  <span
                    className="spinner"
                    aria-hidden="true"
                    style={styles.spinner}
                  ></span>
                  Processing...
                </span>
              ) : (
                "Generate AI Clip"
              )}
            </button>

            {message && (
              <p
                role="alert"
                style={{
                  marginTop: 20,
                  color: message.startsWith("⚠️ Error") || message.startsWith("⚠️ Please") ? "#dc2626" : "#16a34a",
                  fontWeight: "600",
                  lineHeight: 1.5,
                  minHeight: 24,
                  whiteSpace: "pre-line"
                }}
              >
                {message}
              </p>
            )}
          </form>
        </div>
      </main>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    height: "100vh",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    backgroundColor: "#f4f6f9",
    color: "#111827",
    fontSize: 16,
  },
  sidebar: {
    width: "220px",
    backgroundColor: "#111827",
    color: "white",
    padding: "32px 24px",
    display: "flex",
    flexDirection: "column",
    gap: 28,
    userSelect: "none",
  },
  sidebarHeader: {
    marginBottom: 28,
    fontWeight: "700",
    fontSize: "26px",
  },
  navList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "flex",
    flexDirection: "column",
    gap: 18,
  },
  navItem: {
    color: "white",
    cursor: "pointer",
    fontWeight: "600",
    borderRadius: 8,
    padding: "12px 18px",
    transition: "background-color 0.25s ease",
    outline: "none",
  },
  main: {
    flex: 1,
    padding: "56px 60px",
    overflowY: "auto",
    display: "flex",
    justifyContent: "center",
  },
  container: {
    width: "100%",
    maxWidth: 640,
  },
  card: {
    background: "white",
    padding: "44px 48px",
    borderRadius: 16,
    boxShadow: "0 12px 30px rgba(0,0,0,0.12)",
    display: "flex",
    flexDirection: "column",
    gap: 32,
  },
  label: {
    fontWeight: "700",
    fontSize: "15px",
    marginBottom: 8,
    display: "block",
    color: "#374151",
  },
  input: {
    width: "100%",
    padding: "14px 16px",
    marginBottom: 0,
    borderRadius: 8,
    border: "1.8px solid #cbd5e1",
    fontSize: 15,
    boxSizing: "border-box",
    transition: "border-color 0.25s ease, box-shadow 0.25s ease",
    fontFamily: "inherit",
    outlineOffset: 2,
  },
  helpText: {
    fontSize: 13,
    color: "#6b7280",
    marginTop: 6,
    marginBottom: 18,
    fontWeight: 400,
  },
  timeInputsWrapper: {
    display: "flex",
    gap: 32,
    marginBottom: 26,
  },
  timeInputContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
  button: {
    width: "100%",
    padding: "18px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: 12,
    fontSize: 17,
    fontWeight: "700",
    transition: "background-color 0.3s ease",
    userSelect: "none",
    boxShadow:
      "0 4px 8px rgba(37, 99, 235, 0.4), 0 1px 2px rgba(0, 0, 0, 0.1)",
  },
  spinner: {
    display: "inline-block",
    width: 20,
    height: 20,
    border: "3px solid rgba(255, 255, 255, 0.6)",
    borderTopColor: "#fff",
    borderRadius: "50%",
    marginRight: 12,
    verticalAlign: "middle",
    animation: "spin 1s linear infinite",
  },
};

export default App;