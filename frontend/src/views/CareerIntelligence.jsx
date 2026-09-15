import React, { useEffect, useState } from 'react'
import { ArrowRight, Brain, Compass, TrendingUp } from 'lucide-react'
import apiClient from '../api/config'

export default function CareerIntelligence() {
  const [data, setData] = useState({
    career_signal: 'Professional identity',
    strong_evidence: [],
    next_gaps: [],
    summary: 'AVIS is still learning from your verified profile and training data.',
    ai_recommendation: null,
  })

  useEffect(() => {
    let active = true
    apiClient
      .get('/api/ai/career-intelligence')
      .then((res) => {
        if (active) setData(res.data)
      })
      .catch(() => {
        if (active) setData({
          career_signal: 'Profile not yet ready',
          strong_evidence: [],
          next_gaps: ['Add verified profile evidence'],
          summary: 'No live intelligence is available until profile data or a CV is uploaded.',
          ai_recommendation: null,
        })
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CAREER INTELLIGENCE</div>
          <h1>Where your profile is strongest</h1>
        </div>
      </div>

      <div className="panel intelligence-hero">
        <div className="signal-row strong">
          <Compass size={16} />
          <span>{data.career_signal}</span>
        </div>
        <p>{data.summary}</p>
      </div>

      <div className="split-panel">
        <div className="panel">
          <div className="mini-label">STRONG EVIDENCE</div>
          {data.strong_evidence.length === 0 ? (
            <p>No strong evidence is available yet. Add a CV or training update to improve the signal.</p>
          ) : (
            <ul className="check-list">
              {data.strong_evidence.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel">
          <div className="mini-label">NEXT GAP</div>
          <h3>{data.next_gaps[0] || 'Add evidence'}</h3>
          <p>{data.next_gaps.length ? 'This is the next signal AVIS suggests you strengthen.' : 'No gap is currently identified from your available evidence.'}</p>
          <button type="button" className="text-button">
            Explore learning path <ArrowRight size={14} />
          </button>
        </div>
      </div>

      <div className="panel insight-panel compact">
        <div className="signal-row">
          <TrendingUp size={16} />
          <span>{data.ai_recommendation?.current_intent || 'Career momentum is based on the latest verified evidence.'}</span>
        </div>
        <div className="signal-row muted">
          <Brain size={16} />
          <span>{data.ai_recommendation?.target_role || 'AVIS will suggest a more specific plan as more evidence is added.'}</span>
        </div>
      </div>
    </div>
  )
}
