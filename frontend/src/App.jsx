import { useState, useEffect } from "react";

function App() {
  const [companies, setCompanies] = useState([]);
  const [file, setFile] = useState(null);

  // Fetch data from FastAPI
  const refreshData = () => {
    fetch("http://localhost:8000/companies")
      .then((res) => res.json())
      .then((data) => setCompanies(data))
      .catch((err) => console.error("Backend offline"));
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 3000); // Auto-refresh every 3s
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async () => {
    if (!file) return alert("Select a CSV first!");
    const formData = new FormData();
    formData.append("file", file);

    await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData,
    });
    alert("Upload Success! Processing...");
  };

  return (
    <div
      style={{
        padding: "50px",
        fontFamily: "sans-serif",
        maxWidth: "800px",
        margin: "auto",
      }}
    >
      <h1 style={{ color: "#2563eb" }}>🚀 AI GTM Enrichment</h1>

      <div
        style={{
          background: "#f3f4f6",
          padding: "20px",
          borderRadius: "8px",
          marginBottom: "20px",
        }}
      >
        <h3>Upload Leads (CSV)</h3>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button
          onClick={handleUpload}
          style={{ marginLeft: "10px", padding: "8px 16px", cursor: "pointer" }}
        >
          Start Enrichment
        </button>
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: "#e5e7eb" }}>
            <th style={{ padding: "10px", border: "1px solid #ddd" }}>
              Domain
            </th>
            <th style={{ padding: "10px", border: "1px solid #ddd" }}>
              Industry
            </th>
            <th style={{ padding: "10px", border: "1px solid #ddd" }}>Size</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(companies) && companies.length > 0 ? (
            companies.map((c) => (
              <tr key={c.id}>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {c.domain}
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {c.industry}
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {c.size || "-"}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="3" style={{ textAlign: "center", padding: "20px" }}>
                No leads found. Upload a CSV to start!
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
