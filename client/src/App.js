import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);  
    });

    try {
      const res = await axios.post('http://localhost:8000/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(res.data);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>SortPics</h1>
      <input type="file" multiple onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>

      <div style={{ marginTop: 20 }}>
        {results.map((res, idx) => (
          <div key={idx} style={{ marginBottom: 10 }}>
            <strong>{res.filename}</strong>
            <p><em>{res.caption}</em></p>
            <p><strong>Categories:</strong> {res.tags.content}</p>
            <hr />
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
