import React, { useState } from 'react';
import { cvService } from '../services/cvService';
import { Card } from '../components/Card';
import { Loader } from '../components/Loader';

export default function CV() {
  const [cv, setCv] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);
  const [evaluating, setEvaluating] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await cvService.get();
      setCv(data);
    } catch (err) {
      setError(err?.message || 'Failed to load CV');
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    load();
  }, []);

  const onFile = (e) => setFile(e.target.files?.[0] || null);

  const evaluate = async () => {
    if (!file) return;
    setEvaluating(true);
    setError(null);
    try {
      const fd = new FormData();
      fd.append('file', file);
      const res = await cvService.evaluate(fd);
      setCv(res);
    } catch (err) {
      setError(err?.message || 'Evaluation failed');
    } finally {
      setEvaluating(false);
    }
  };

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">CV</h1>
          <div className="p-muted">View and evaluate your CV</div>
        </div>
      </div>

      <div className="grid cols-2" style={{ marginTop: 12 }}>
        <Card title="CV Overview">
          {loading ? <Loader /> : error ? <div role="alert">{error}</div> : cv ? (
            <div>
              <div style={{ fontWeight: 700 }}>{cv.title || 'My CV'}</div>
              <div className="small">Score: <span className="badge">{cv.score || 0}</span></div>
              <div style={{ marginTop: 12 }}>
                <h4 className="small">Strengths</h4>
                <ul>{(cv.strengths || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
                <h4 className="small">Improvements</h4>
                <ul>{(cv.improvements || []).map((s, i) => <li key={i}>{s}</li>)}</ul>
              </div>
            </div>
          ) : <div>No CV uploaded yet</div>}
        </Card>

        <Card title="Evaluate CV">
          <div>
            <input type="file" accept=".pdf,.doc,.docx" onChange={onFile} />
            <div style={{ marginTop: 12 }}>
              <button className="btn" onClick={evaluate} disabled={!file || evaluating}>{evaluating ? 'Evaluating...' : 'Evaluate CV'}</button>
            </div>
            {error && <div role="alert" style={{ color: '#d14343', marginTop: 8 }}>{error}</div>}
          </div>
        </Card>
      </div>
    </div>
  );
}
