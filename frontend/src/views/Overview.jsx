import React, { useState } from 'react'
import { Link } from 'react-router-dom'

function Card({ title, value, children }) {
  return (
    <div className="panel p-4 rounded-lg bg-[#191915] border border-[rgba(243,241,233,0.12)]">
      <div className="text-sm text-[rgba(243,241,233,0.6)]">{title}</div>
      <div className="text-2xl font-semibold mt-1 text-[#F3F1E9]">{value || '—'}</div>
      {children}
    </div>
  )
}

export default function Overview({ stats, applications = [], onAddTraining, onApply }) {
  const [trainingInput, setTrainingInput] = useState('')

  const handleSubmitTraining = (e) => {
    e.preventDefault()
    if (!trainingInput.trim()) return
    if (onAddTraining) onAddTraining(trainingInput)
    setTrainingInput('')
  }

  return (
    <div className="space-y-6 text-[#F3F1E9]">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card title="AI Knowledge Base" value={stats?.knowledgeBaseCount ?? '—'} />
        <Card title="Active Job Matches" value={stats?.activeMatchesCount ?? '—'} />
        <Card title="Top Match Score" value={stats?.topMatchScore ? `${stats.topMatchScore}%` : '—'} />
        <Card title="CV Readiness" value={stats?.cvReadiness ? `${stats.cvReadiness}%` : '—'} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="panel p-4 rounded-lg bg-[#191915] border border-[rgba(243,241,233,0.12)] flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-semibold">Training & Twin Context</h3>
            <textarea
              value={trainingInput}
              onChange={(e) => setTrainingInput(e.target.value)}
              className="w-full mt-3 p-3 rounded bg-[#0E0E0C] border border-[rgba(243,241,233,0.12)] text-[#F3F1E9] focus:outline-none focus:border-[#D96A1C]"
              rows={5}
              placeholder="Add experience or training context for the AI..."
            />
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={handleSubmitTraining}
              className="px-4 py-2 bg-[#D96A1C] text-white rounded hover:bg-[#c25e17] transition-colors"
            >
              Submit
            </button>
            <Link
              to="/chat"
              className="px-4 py-2 border border-[rgba(243,241,233,0.12)] rounded hover:bg-[rgba(243,241,233,0.05)] transition-colors inline-block text-center"
            >
              Open Chat
            </Link>
          </div>
        </div>

        <div className="panel p-4 rounded-lg bg-[#191915] border border-[rgba(243,241,233,0.12)]">
          <h3 className="text-lg font-semibold mb-3">Career Applications Stream</h3>
          
          {applications.length > 0 ? (
            <div className="space-y-3">
              {applications.map((app) => (
                <div
                  key={app.id || app.title}
                  className="p-3 rounded border border-[rgba(243,241,233,0.12)] flex justify-between items-center bg-[#0E0E0C]"
                >
                  <div>
                    <div className="font-semibold">{app.title} — {app.company}</div>
                    <div className="text-sm text-[rgba(243,241,233,0.6)]">
                      Matching skills: {Array.isArray(app.skills) ? app.skills.join(', ') : app.skills || 'N/A'}
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <div className="text-[#D96A1C] font-bold">{app.matchScore}%</div>
                    <button
                      onClick={() => onApply && onApply(app.id)}
                      className="mt-2 px-3 py-1 rounded bg-[#D96A1C] text-white text-sm hover:bg-[#c25e17] transition-colors"
                    >
                      Apply Now
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-[rgba(243,241,233,0.5)] py-8 text-center">
              No active job application streams found.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}