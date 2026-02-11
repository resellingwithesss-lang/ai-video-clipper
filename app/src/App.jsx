import axios from "axios";
import { useState } from "react";

export default function App() {
  const [url, setUrl] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const API = "https://ai-clipper-backend.onrender.com";

  const generateClip = async () => {
    try {
      setLoading(true);
      setDownloadUrl("");

      const res = await axios.post(`${API}/clip`, null, {
        params: {
          url: url.trim(),
          start: "0",
          end: "10",
        },
      });

      setDownloadUrl(res.data.download_url);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Error generating clip");
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "100px" }}>
      <h1>AI Video Clipper</h1>

      <input
        style={{ width: 400, padding: 10 }}
        placeholder="Paste YouTube URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <br /><br />

      <button onClick={generateClip} disabled={loading}>
        {loading ? "Generating..." : "Generate Clip"}
      </button>

      <br /><br />

      {downloadUrl && (
        <a href={downloadUrl} target="_blank">
          Download Clip
        </a>
      )}
    </div>
  );
}
