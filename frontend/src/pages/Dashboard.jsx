import React from 'react';
import { useApiState } from '../hooks/useApiState';
import { profileService } from '../services/profileService';
import { jobsService } from '../services/jobsService';
import { trainingService } from '../services/trainingService' || {};
import { Card } from '../components/Card';
import { Loader } from '../components/Loader';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const profileState = useApiState(() => profileService.get(), []);
  const jobsState = useApiState(() => jobsService.list({ limit: 6 }), []);
  // trainingService may not exist in your repo; handle gracefully
  const trainingState = useApiState(() => (trainingService?.list ? trainingService.list() : Promise.resolve([])), []);

  return (
    <div>
      <div className="header-row">
        <div>
          <h1 className="h1">Dashboard</h1>
          <div className="p-muted">Overview of your profile, jobs and training</div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Link to="/cv" className="btn ghost">My CV</Link>
          <Link to="/cv-writer" className="btn">CV Writer</Link>
        </div>
      </div>

      <div className="grid cols-3" style={{ marginTop: 18 }}>
        <Card title="Profile">
          {profileState.loading ? <Loader /> : profileState.error ? (
            <div role="alert">Unable to load profile. <button className="btn ghost" onClick={() => window.location.reload()}>Retry</button></div>
          ) : profileState.empty ? (
            <div>No profile yet. <Link to="/profile">Create profile</Link></div>
          ) : (
            <div>
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div className="avatar" aria-hidden>{profileState.data.first_name?.[0] || 'U'}</div>
                <div>
                  <div style={{ fontWeight: 700 }}>{profileState.data.first_name} {profileState.data.last_name}</div>
                  <div className="small">{profileState.data.headline || 'No headline yet'}</div>
                </div>
              </div>
              <div style={{ marginTop: 12 }}>
                <div className="small">Profile completion</div>
                <div style={{ marginTop: 6 }}>
                  <div style={{ height: 10, background: '#eee', borderRadius: 8 }}>
                    <div style={{ width: `${profileState.data.completion || 40}%`, height: 10, background: 'var(--accent)', borderRadius: 8 }} />
                  </div>
                </div>
              </div>
            </div>
          )}
        </Card>

        <Card title="Recommended jobs">
          {jobsState.loading ? <Loader /> : jobsState.error ? (
            <div role="alert">Unable to load jobs.</div>
          ) : jobsState.empty ? (
            <div>No jobs found</div>
          ) : (
            <div style={{ display: 'grid', gap: 10 }}>
              {jobsState.data.slice(0,3).map((job) => (
                <div key={job.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700 }}>{job.title}</div>
                    <div className="small">{job.company} • {job.location}</div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <div className="badge">{Math.round((job.match || 0))}%</div>
                    <Link to={`/jobs/${job.id}`} className="btn ghost">View</Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card title="Training">
          {trainingState.loading ? <Loader /> : trainingState.error ? (
            <div role="alert">Unable to load training.</div>
          ) : trainingState.empty ? (
            <div>No training assigned</div>
          ) : (
            <div style={{ display: 'grid', gap: 10 }}>
              {trainingState.data.slice(0,3).map((c, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 700 }}>{c.title}</div>
                    <div className="small">{c.provider}</div>
                  </div>
                  <div style={{ minWidth: 120 }}>
                    <div style={{ height: 8, background: '#eee', borderRadius: 8 }}>
                      <div style={{ width: `${c.progress || 0}%`, height: 8, background: 'var(--accent)', borderRadius: 8 }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
