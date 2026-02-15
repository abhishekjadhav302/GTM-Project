import { useState, useEffect } from "react";

function App() {
  const [companies, setCompanies] = useState([]);
  const [file, setFile] = useState(null);

  const refreshData = () => {
    fetch("http://localhost:8000/companies")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setCompanies(data);
        }
      })
      .catch((err) => console.error("Backend offline"));
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async () => {
    if (!file) return alert("Select a CSV first!");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (response.ok) {
        alert("Upload Success! Your cloud database is being updated.");
        refreshData(); // Immediate refresh after upload
      } else {
        alert("Upload failed. Check your CSV format.");
      }
    } catch (error) {
      console.error("Upload error:", error);
    }
  };

  return (
    <div
      style={{
        padding: "50px",
        fontFamily: "sans-serif",
        maxWidth: "900px",
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
        <h3>Step 1: Upload leads.csv (Header must be 'domain')</h3>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button
          onClick={handleUpload}
          style={{
            marginLeft: "10px",
            padding: "8px 16px",
            cursor: "pointer",
            background: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "4px",
          }}
        >
          Run Enrichment
        </button>
      </div>

      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}
      >
        <thead>
          <tr style={{ background: "#e5e7eb" }}>
            <th style={{ padding: "12px", border: "1px solid #ddd" }}>
              Domain
            </th>
            <th style={{ padding: "12px", border: "1px solid #ddd" }}>
              Industry
            </th>
            <th style={{ padding: "12px", border: "1px solid #ddd" }}>Size</th>
          </tr>
        </thead>
        <tbody>
          {companies.length > 0 ? (
            companies.map((c) => (
              <tr key={c.id}>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {c.domain}
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {c.industry}
                </td>
                <td style={{ padding: "10px", border: "1px solid #ddd" }}>
                  {c.size}
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td
                colSpan="3"
                style={{ textAlign: "center", padding: "30px", color: "#666" }}
              >
                Database Empty. Please upload a valid CSV.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default App;
