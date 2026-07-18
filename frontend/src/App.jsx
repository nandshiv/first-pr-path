import { useState, useEffect } from "react";

function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/db-check")
      .then((response) => response.json())
      .then((data) => {
        setStatus(`${data.database}, result: ${data.result}`);
      })
      .catch((error) => {
        setStatus("failed to reach backend");
      });
  }, []);

  return (
    <div>
      <h1>First PR Path</h1>
      <p>Backend status: {status}</p>
    </div>
  );
}

export default App;
