import React, { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [start, setStart] = useState("00:00:00");
  const [end, setEnd] = useState("00:00:30");
  const [quality, setQuality] = useState("1080p");
  const [style, setStyle] = useState("Standard");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
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
      window.open(`http://localhost:8000/download/${data.job_id}`);
    } catch (err) {
      setMessage("⚠️ Error: " + err.message);
    }

    setLoading(false);
  };

  return (
    <div style={styles.page}>
      <nav style={styles.sidebar} aria-label="Primary">
        <h2 style={styles.sidebarHeader}>🎬 Creator AI</h2>
        <ul style={styles.navList}>
          <li
            style={styles.navItem}
            tabIndex={0}
            role="link"
            aria-label="Dashboard"
            onKeyDown={(e) => e.key === "Enter" && e.currentTarget.click()}
          >
            Dashboard
          </li>
          <li
            style={styles.navItem}
            tabIndex={0}
            role="link"
            aria-label="My Clips"
            onKeyDown={(e) => e.key === "Enter" && e.currentTarget.click()}
          >
            My Clips
          </li>
          <li
            style={styles.navItem}
            tabIndex={0}
            role="link"
            aria-label="Analytics"
            onKeyDown={(e) => e.key === "Enter" && e.currentTarget.click()}
          >
            Analytics
          </li>
          <li
            style={styles.navItem}
            tabIndex={0}
            role="link"
            aria-label="AI Tools"
            onKeyDown={(e) => e.key === "Enter" && e.currentTarget.click()}
          >
            AI Tools
          </li>
        </ul>
      </nav>

      <main style={styles.main}>
        <h1 style={{ marginBottom: 28 }}>AI Clip Generator Studio</h1>

        <form
          onSubmit={handleSubmit}
          style={styles.card}
          aria-live="polite"
          aria-busy={loading}
          noValidate
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
            style={styles.input}
            aria-describedby="urlHelp"
            disabled={loading}
            autoComplete="off"
            autoFocus
          />
          <small id="urlHelp" style={styles.helpText}>
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
                onChange={(e) => setStart(e.target.value)}
                style={styles.input}
                max={end}
                aria-describedby="startHelp"
                disabled={loading}
                pattern="\d{2}:\d{2}:\d{2}"
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
                onChange={(e) => setEnd(e.target.value)}
                style={styles.input}
                min={start}
                aria-describedby="endHelp"
                disabled={loading}
                pattern="\d{2}:\d{2}:\d{2}"
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
          >
            <option>1080p</option>
            <option>720p</option>
            <option>4K</option>
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
          >
            <option>Standard</option>
            <option>Viral Optimized</option>
            <option>Shorts Format</option>
            <option>Podcast Cut</option>
          </select>

          <button
            type="submit"
            disabled={loading || !url.trim()}
            style={{
              ...styles.button,
              opacity: loading ? 0.7 : 1,
              cursor: loading ? "not-allowed" : "pointer",
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
                marginTop: 15,
                color: message.startsWith("⚠️ Error") ? "#dc2626" : "#16a34a",
                fontWeight: "600",
                lineHeight: 1.4,
              }}
            >
              {message}
            </p>
          )}
        </form>
      </main>
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    height: "100vh",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#f4f6f9",
    color: "#111827",
  },
  sidebar: {
    width: "220px",
    backgroundColor: "#111827",
    color: "white",
    padding: "30px 20px",
    display: "flex",
    flexDirection: "column",
    gap: 24,
  },
  sidebarHeader: {
    marginBottom: 24,
    fontWeight: "bold",
    fontSize: "24px",
  },
  navList: {
    listStyle: "none",
    padding: 0,
    margin: 0,
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  navItem: {
    color: "white",
    cursor: "pointer",
    fontWeight: "500",
    borderRadius: 6,
    padding: "10px 14px",
    userSelect: "none",
    transition: "background-color 0.2s ease",
    outline: "none",
  },
  main: {
    flex: 1,
    padding: "50px 56px",
    overflowY: "auto",
    display: "flex",
    justifyContent: "center",
  },
  card: {
    background: "white",
    padding: "36px 40px",
    borderRadius: "12px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
    maxWidth: "600px",
    display: "flex",
    flexDirection: "column",
  },
  label: {
    fontWeight: "600",
    fontSize: "14px",
    marginBottom: 8,
    display: "block",
  },
  input: {
    width: "100%",
    padding: "12px 14px",
    marginBottom: "22px",
    borderRadius: "6px",
    border: "1px solid #ddd",
    fontSize: "14px",
    boxSizing: "border-box",
    transition: "border-color 0.2s ease",
  },
  helpText: {
    fontSize: "12px",
    color: "#6b7280",
    marginTop: "-18px",
    marginBottom: "14px",
  },
  timeInputsWrapper: {
    display: "flex",
    gap: "22px",
    marginBottom: "25px",
  },
  timeInputContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
  button: {
    width: "100%",
    padding: "16px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "600",
    transition: "background-color 0.3s ease",
    userSelect: "none",
  },
  spinner: {
    display: "inline-block",
    width: 18,
    height: 18,
    border: "3px solid rgba(255, 255, 255, 0.6)",
    borderTopColor: "#fff",
    borderRadius: "50%",
    marginRight: 10,
    verticalAlign: "middle",
    animation: "spin 1s linear infinite",
  },
};

export default App;