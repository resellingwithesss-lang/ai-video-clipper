import axios from "axios";
import { useState } from "react";

export default function App() {
  const [url,setUrl]=useState("");
  const [start,setStart]=useState("0");
  const [end,setEnd]=useState("10");
  const [status,setStatus]=useState("");

  const API="https://ai-clipper-backend.onrender.com";

  const generateClip=async()=>{
    setStatus("Starting job...");
    const res=await axios.post(`${API}/clip`,null,{
      params:{url,start,end}
    });

    const job=res.data.job_id;
    setStatus("Processing video...");

    const poll=setInterval(async()=>{
      const s=await axios.get(`${API}/status/${job}`);
      if(s.data.status==="done"){
        clearInterval(poll);
        window.open(`${API}/download/${job}`,"_blank");
        setStatus("Done!");
      }
    },3000);
  };

  return (
    <div style={{textAlign:"center",marginTop:100}}>
      <h1>AI Video Clipper</h1>

      <input placeholder="YouTube URL"
        value={url} onChange={e=>setUrl(e.target.value)} />

      <br/><br/>

      Start seconds:
      <input value={start} onChange={e=>setStart(e.target.value)} />

      End seconds:
      <input value={end} onChange={e=>setEnd(e.target.value)} />

      <br/><br/>
      <button onClick={generateClip}>Generate</button>

      <p>{status}</p>
    </div>
  );
}
