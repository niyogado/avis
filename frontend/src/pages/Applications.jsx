import React from 'react';
import { useApiState } from '../hooks/useApiState';
import { Card } from '../components/Card';
import { applicationsService } from '../services/applicationsService' || {};

export default function Applications() {
  const { loading, data, error, empty } = useApiState(() => (applicationsService?.list ? applicationsService.list() : Promise.resolve([])), []);

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">Applications</h1>
          <div className="p-muted">Track your job applications</div>
        </div>
      </div>

      <Card>
        {loading ? <div>Loading...</div> : error ? <div role="alert">Failed to load applications</div> : empty ? <div>No applications yet</div> : (
          <div style={{ display: 'grid', gap: 12 }}>
            {data.map((a) => (
              <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{a.job_title}</div>
                  <div className="small">{a.company}</div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <div className="small">{a.status}</div>
                  <div className="badge">{Math.round(a.match || 0)}%</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
