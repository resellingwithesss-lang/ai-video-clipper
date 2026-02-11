import { useState } from "react";
import axios from "axios";
import "./App.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const generateClip = async () => {
    try {
      setLoading(true);
      setDownloadUrl("");

      const res = await axios.post("http://localhost:8000/clip", null, {
        params: {
          url: url,
          start: "0",
          end: "10"
        }
      });

      setDownloadUrl(res.data.download_url);
      setLoading(false);

    } catch (err) {
      setLoading(false);
      alert("Error generating clip");
    }
  };

  // REAL FILE DOWNLOAD (fixes blocked tab issue)
  const downloadClip = async () => {
    const response = await fetch(downloadUrl);
    const blob = await response.blob();

    const fileUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = fileUrl;
    a.download = "clip.mp4";
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  return (
    <div className="container">
      <h1>AI Video Clipper</h1>

      <input
        placeholder="Paste YouTube link"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <br />

      <button onClick={generateClip} disabled={loading}>
        {loading ? "Generating..." : "Generate AI Clip"}
      </button>

      {downloadUrl && (
        <>
          <br />
          <button onClick={downloadClip}>
            Download Clip
          </button>
        </>
      )}
    </div>
  );
}
