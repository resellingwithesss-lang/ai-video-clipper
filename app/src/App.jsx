import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [url, setUrl] = useState("");
  const [clipDuration, setClipDuration] = useState(30);
  const [phase, setPhase] = useState("input"); // input | processing | results
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const pollRef = useRef(null);

  const isValidUrl = (v) =>
    /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)\S+/.test(
      v.trim()
    );

  // ----- submit -----
  const handleSubmit = async () => {
    if (!isValidUrl(url)) return;
    setError("");
    setPhase("processing");
    setJob({
      status: "downloading",
      completed_clips: 0,
      total_clips: 0,
      clips: [],
      video_title: "",
    });

    try {
      const res = await fetch(`${API_BASE}/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), clip_duration: clipDuration }),
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || "Failed to start processing");
      }
      const { job_id } = await res.json();
      startPolling(job_id);
    } catch (err) {
      setError(err.message);
      setPhase("input");
    }
  };

  // ----- polling -----
  const startPolling = (jobId) => {
    const poll = async () => {
      try {
        const res = await fetch(`${API_BASE}/jobs/${jobId}`);
        const data = await res.json();
        setJob(data);
        if (data.status === "done") {
          setPhase("results");
          return;
        }
        if (data.status === "error") {
          setError(data.error || "Processing failed");
          setPhase("input");
          return;
        }
      } catch {
        /* retry */
      }
      pollRef.current = setTimeout(poll, 1500);
    };
    poll();
  };

  useEffect(() => {
    return () => {
      if (pollRef.current) clearTimeout(pollRef.current);
    };
  }, []);

  const reset = () => {
    if (pollRef.current) clearTimeout(pollRef.current);
    setUrl("");
    setPhase("input");
    setJob(null);
    setError("");
  };

  const fmt = (s) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  // ===================== RENDER =====================

  return (
    <div className="app">
      {/* ---- header ---- */}
      <header className="header">
        <div className="logo" onClick={reset}>
          <span className="logo-icon">&#9654;</span>
          <span className="logo-text">ClipForge</span>
        </div>
        {phase !== "input" && (
          <button className="header-btn" onClick={reset}>
            + New Project
          </button>
        )}
      </header>

      <div className="content">
        {/* ==================== INPUT ==================== */}
        {phase === "input" && (
          <div className="input-phase fade-in">
            <div className="hero">
              <h1 className="hero-title">
                Turn any video into
                <span className="gradient-text">
                  {" "}
                  viral short-form content
                </span>
              </h1>
              <p className="hero-sub">
                Paste a YouTube link. Get perfectly cropped 9:16 vertical clips
                ready for TikTok, Reels &amp; Shorts.
              </p>
            </div>

            <div className="input-card">
              <input
                className={`url-input ${url && !isValidUrl(url) ? "url-input--invalid" : ""}`}
                type="url"
                value={url}
                onChange={(e) => {
                  setUrl(e.target.value);
                  setError("");
                }}
                placeholder="https://youtube.com/watch?v=..."
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                autoFocus
              />

              {url && !isValidUrl(url) && (
                <p className="url-error">Enter a valid YouTube URL</p>
              )}

              <div className="options-row">
                <div className="option-group">
                  <span className="option-label">Clip Length</span>
                  <div className="pill-group">
                    {[
                      { value: 30, label: "30 s" },
                      { value: 60, label: "60 s" },
                      { value: 90, label: "90 s" },
                    ].map((d) => (
                      <button
                        key={d.value}
                        type="button"
                        className={`pill ${clipDuration === d.value ? "pill--active" : ""}`}
                        onClick={() => setClipDuration(d.value)}
                      >
                        {d.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="option-group">
                  <span className="option-label">Format</span>
                  <div className="badge">9:16 Vertical</div>
                </div>

                <div className="option-group">
                  <span className="option-label">Export</span>
                  <div className="badge">1080 &times; 1920</div>
                </div>
              </div>

              <button
                className="submit-btn"
                onClick={handleSubmit}
                disabled={!url.trim() || !isValidUrl(url)}
              >
                Generate Clips
              </button>

              {error && <p className="error-msg">{error}</p>}
            </div>

            <div className="features">
              {[
                {
                  icon: "\u26A1",
                  title: "Auto-Split",
                  desc: "Splits the full video into multiple short clips automatically",
                },
                {
                  icon: "\uD83D\uDCD0",
                  title: "9:16 Reframe",
                  desc: "Center-cropped vertical format for every platform",
                },
                {
                  icon: "\uD83C\uDFAC",
                  title: "Studio Quality",
                  desc: "1080\u00D71920 H.264 with 192 kbps AAC audio",
                },
              ].map((f) => (
                <div key={f.title} className="feature-card">
                  <span className="feature-icon">{f.icon}</span>
                  <strong className="feature-title">{f.title}</strong>
                  <span className="feature-desc">{f.desc}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ==================== PROCESSING ==================== */}
        {phase === "processing" && job && (
          <div className="processing-phase fade-in">
            <div className="processing-card">
              <div className="spinner-wrap">
                <div className="spinner-ring" />
              </div>

              <h2 className="processing-title">
                {job.status === "downloading"
                  ? "Downloading video\u2026"
                  : "Creating your clips\u2026"}
              </h2>

              {job.video_title && (
                <p className="video-title">{job.video_title}</p>
              )}

              {job.status === "processing" && job.total_clips > 0 && (
                <>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${(job.completed_clips / job.total_clips) * 100}%`,
                      }}
                    />
                  </div>
                  <p className="progress-text">
                    {job.completed_clips} of {job.total_clips} clips ready
                  </p>
                </>
              )}

              {job.status === "downloading" && (
                <p className="progress-text">
                  Fetching from YouTube&hellip; this may take a moment.
                </p>
              )}
            </div>
          </div>
        )}

        {/* ==================== RESULTS ==================== */}
        {phase === "results" && job && (
          <div className="results-phase fade-in">
            <div className="results-header">
              <div>
                <h2 className="results-title">
                  {job.clips.length} clips ready
                </h2>
                {job.video_title && (
                  <p className="results-subtitle">{job.video_title}</p>
                )}
              </div>
              <a
                href={`${API_BASE}/clips/${job.job_id}/download-all`}
                className="download-all-btn"
              >
                <span className="dl-icon">&#8595;</span> Download All (.zip)
              </a>
            </div>

            <div className="clips-grid">
              {job.clips.map((clip) => (
                <div key={clip.index} className="clip-card">
                  <div className="clip-visual">
                    <span className="clip-number">#{clip.index + 1}</span>
                    <div className="clip-aspect">9:16</div>
                  </div>
                  <div className="clip-body">
                    <div className="clip-times">
                      <span>
                        {fmt(clip.start)} &ndash;{" "}
                        {fmt(clip.start + clip.duration)}
                      </span>
                      <span className="clip-dur">{clip.duration}s</span>
                    </div>
                    <span className="clip-spec">1080&times;1920 &middot; H.264</span>
                    <a
                      href={`${API_BASE}/clips/${job.job_id}/${clip.index}`}
                      className="clip-dl-btn"
                    >
                      Download
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
