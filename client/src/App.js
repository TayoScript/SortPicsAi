import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false); 

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    try {
      setLoading(true); 
      const res = await axios.post('http://localhost:8000/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResults(res.data);
    } catch (err) {
      console.error('Upload failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const groupedBySmartLabel = results.reduce((acc, item) => {
    const label = item.group_label || 'Uncategorized';
    if (!acc[label]) acc[label] = [];
    acc[label].push(item);
    return acc;
  }, {});

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>SortPics</h1>

      <input type="file" multiple accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} style={{ marginLeft: 10 }}>Upload</button>

     
      {loading && (
        <div style={{ marginTop: '2rem', fontSize: '1.5rem', textAlign: 'center' }}>
          ⏳ Processing images
        </div>
      )}

      
      {!loading && results.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          {Object.entries(groupedBySmartLabel).map(([label, items], idx) => (
            <div key={idx} style={{ marginBottom: '3rem' }}>
              <h2 style={{ color: '#2c3e50', textTransform: 'capitalize' }}>{label}</h2>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem' }}>
                {items.map((img, imgIdx) => (
                  <div key={imgIdx} style={{ width: '200px', textAlign: 'center' }}>
                    {img.url && (
                      <img 
                        src={img.url} 
                        alt={img.filename} 
                        style={{
                          width: '100%',
                          height: '150px',
                          objectFit: 'cover',
                          borderRadius: '8px',
                          marginBottom: '0.5rem',
                          boxShadow: '0 4px 8px rgba(0,0,0,0.1)'
                        }}
                      />
                    )}
                    <strong style={{ fontSize: '1rem' }}>{img.filename}</strong>
                    <p style={{ fontSize: '0.9em', color: '#555' }}>
                      <em>{img.caption}</em>
                    </p>
                  </div>
                ))}
              </div>
              <hr style={{ marginTop: '2rem' }} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
