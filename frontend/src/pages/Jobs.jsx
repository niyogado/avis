import React from 'react';
import { jobsService } from '../services/jobsService';
import { useApiState } from '../hooks/useApiState';
import { Card } from '../components/Card';
import { Link } from 'react-router-dom';

export default function Jobs() {
  const { loading, data, error, empty } = useApiState(() => jobsService.list({ limit: 20 }), []);

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">Jobs</h1>
          <div className="p-muted">Browse job opportunities</div>
        </div>
      </div>

      <Card>
        {loading ? <div>Loading jobs...</div> : error ? <div role="alert">Failed to load jobs</div> : empty ? <div>No jobs available</div> : (
          <div style={{ display: 'grid', gap: 12 }}>
            {data.map((job) => (
              <div key={job.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{job.title}</div>
                  <div className="small">{job.company} • {job.location}</div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <div className="badge">{Math.round(job.match || 0)}%</div>
                  <Link to={`/jobs/${job.id}`} className="btn ghost">View</Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
