import React, { useEffect, useState } from "react"

export default function ApiHealth() {
  const [status, setStatus] = useState("checking...")
  useEffect(() => {
    const base = import.meta.env.VITE_API_BASE || "http://localhost:8000"
    fetch(`${base}/api/health`)
      .then(async r => `${r.status} ${r.statusText} – ${await r.text()}`)
      .then(setStatus)
      .catch(e => setStatus(`Error: ${e.message}`))
  }, [])
  return <div><strong>API:</strong> {status}</div>
}
