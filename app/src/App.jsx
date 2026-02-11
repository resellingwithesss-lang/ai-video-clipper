import axios from "axios";
import { useState } from "react";
import "./App.css";

const API = "https://ai-clipper-backend.onrender.com";

export default function App() {
  const [url, setUrl] = useState("");
  const [start, setStart] = useState("0");
  const [end, setEnd] = useState("10");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const pollStatus = async (jobId) => {
    const interval = setInterval(async () => {
      const res = await axios.get(`${API}/status/${jobId}`);
      const jobStatus = res.data.status;
      setStatus(jobStatus);

      if (jobStatus === "complete") {
        clearInterval(interval);
        setLoading(false);
        window.open(`${API}/download/${jobId}`, "_blank");
      }

      if (jobStatus === "error") {
        clearInterval(interval);
        setLoading(false);
        alert("Error creating clip");
      }
    }, 2000);
  };

  const generateClip = async () => {
    if (!url) return alert("Paste a YouTube URL");

    try {
      setLoading(true);
      setStatus("Starting job...");

      const res = await axios.post(`${API}/clip`, null, {
        params: { url, start, end }
      });

      pollStatus(res.data.job_id);
    } catch (err) {
      console.error(err);
      alert("Backend error");
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>🎬 AI Video Clipper</h1>

        <input
          placeholder="Paste YouTube URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <div className="timeRow">
          <input value={start} onChange={(e)=>setStart(e.target.value)} />
          <input value={end} onChange={(e)=>setEnd(e.target.value)} />
        </div>

        <button onClick={generateClip} disabled={loading}>
          {loading ? "Processing..." : "Generate Clip"}
        </button>

        {status && (
          <div className="result">
            <h3>Status:</h3>
            <p>{status}</p>
          </div>
        )}
      </div>
    </div>
  );
}
