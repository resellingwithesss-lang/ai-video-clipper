import axios from "axios";
import { useState } from "react";
import "./App.css";

const API = "https://ai-clipper-backend.onrender.com";

export default function App() {
  const [url, setUrl] = useState("");
  const [start, setStart] = useState("0");
  const [end, setEnd] = useState("10");
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");

  const generateClip = async () => {
    if (!url) {
      alert("Paste a YouTube URL first");
      return;
    }

    try {
      setLoading(true);
      setDownloadUrl("");

      const res = await axios.post(`${API}/clip`, null, {
        params: { url, start, end }
      });

      setDownloadUrl(res.data.download_url);
    } catch (err) {
      console.error(err);
      alert("Clip generation failed");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <div className="card">

        <h1>🎬 AI Video Clipper</h1>
        <p>Create Shorts & TikToks in seconds</p>

        <input
          placeholder="Paste YouTube URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <div className="timeRow">
          <div>
            <label>Start Time (seconds)</label>
            <input
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </div>

          <div>
            <label>End Time (seconds)</label>
            <input
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </div>
        </div>

        <button onClick={generateClip} disabled={loading}>
          {loading ? "Generating Clip..." : "Generate Clip"}
        </button>

        {downloadUrl && (
          <div className="result">
            <h3>✅ Clip Ready</h3>
            <a href={downloadUrl} target="_blank">
              Download Video
            </a>
          </div>
        )}

      </div>
    </div>
  );
}
