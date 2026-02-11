import axios from "axios";
import { useState } from "react";

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const API = "https://ai-clipper-backend.onrender.com";

  const generateClip = async () => {
    if (!url) {
      alert("Paste a YouTube URL first");
      return;
    }

    try {
      setLoading(true);

      const res = await axios.post(`${API}/clip`, null, {
        params: {
          url: url,
          start: "0",
          end: "10",
        },
      });

      // open download automatically
      window.open(res.data.download_url, "_blank");

    } catch (err) {
      console.error(err);
      alert("Error generating clip");
    } finally {
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
    </div>
  );
}
