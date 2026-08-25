import React from 'react';
import { alertsService } from '../services/alertsService';
import { useApiState } from '../hooks/useApiState';
import { Card } from '../components/Card';

export default function Alerts() {
  const { loading, data, error, empty } = useApiState(() => alertsService.list(), []);

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">Job Alerts</h1>
          <div className="p-muted">Manage your job alerts</div>
        </div>
      </div>

      <Card>
        {loading ? <div>Loading...</div> : error ? <div role="alert">Failed to load alerts</div> : empty ? <div>No alerts set</div> : (
          <div style={{ display: 'grid', gap: 12 }}>
            {data.map((a) => (
              <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{a.title}</div>
                  <div className="small">{a.criteria}</div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button className="btn ghost">Edit</button>
                  <button className="btn">Disable</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
