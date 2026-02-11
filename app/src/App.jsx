import axios from "axios";
import { useState } from "react";
import "./App.css";

const API = "https://ai-clipper-backend.onrender.com";

export default function App() {
  const [email,setEmail]=useState("");
  const [user,setUser]=useState("");
  const [url,setUrl]=useState("");
  const [jobs,setJobs]=useState([]);
  const [status,setStatus]=useState("");

  const login = async ()=>{
    const res = await axios.post(`${API}/login`,null,{params:{email}});
    setUser(res.data.user);
    loadHistory(res.data.user);
  };

  const loadHistory = async (u)=>{
    const res = await axios.get(`${API}/history/${u}`);
    setJobs(res.data.jobs);
  };

  const createClip = async ()=>{
    setStatus("starting...");
    const res = await axios.post(`${API}/clip`,null,{
      params:{url,start:"0",end:"10",user}
    });

    const id = res.data.job_id;

    const poll = setInterval(async ()=>{
      const s = await axios.get(`${API}/status/${id}`);
      setStatus(s.data.status);
      if(s.data.status==="complete"){
        clearInterval(poll);
        window.open(`${API}/download/${id}`);
        loadHistory(user);
      }
    },2000);
  };

  if(!user)
    return (
      <div className="container">
        <div className="card">
          <h1>Login</h1>
          <input placeholder="Email" onChange={e=>setEmail(e.target.value)}/>
          <button onClick={login}>Enter</button>
        </div>
      </div>
    );

  return (
    <div className="container">
      <div className="card">
        <h1>AI Clipper Dashboard</h1>

        <input placeholder="YouTube URL" onChange={e=>setUrl(e.target.value)}/>
        <button onClick={createClip}>Create Clip</button>
        <p>{status}</p>

        <h3>Your Clips</h3>
        {jobs.map(j=>(
          <div key={j}>
            <a href={`${API}/download/${j}`} target="_blank">Download {j}</a>
          </div>
        ))}
      </div>
    </div>
  );
}
