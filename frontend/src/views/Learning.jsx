import React, { useEffect, useState } from 'react'
import { ArrowRight, BookOpen, CheckCircle2, Clock3 } from 'lucide-react'
import apiClient from '../api/config'

export default function Learning() {
  const [lessons, setLessons] = useState([])

  useEffect(() => {
    let active = true
    apiClient
      .get('/api/ai/career-intelligence')
      .then((res) => {
        const gaps = res.data?.next_gaps || []
        const mapped = gaps.length
          ? gaps.map((gap, index) => ({
              title: gap,
              reason: `This gap is currently the clearest improvement for your ${res.data?.career_signal || 'career signal'}.`,
              status: index === 0 ? 'Recommended' : 'Suggested',
              duration: index === 0 ? '4 weeks' : '2 weeks',
            }))
          : [{
              title: 'Add more profile evidence',
              reason: 'AVIS needs a stronger proof base before recommending a learning plan.',
              status: 'Queued',
              duration: 'Variable',
            }]

        if (active) setLessons(mapped)
      })
      .catch(() => {
        if (active) setLessons([{ title: 'No roadmap available yet', reason: 'Upload a CV or add training notes to unlock personalized learning recommendations.', status: 'Waiting', duration: 'Variable' }])
      })

    return () => { active = false }
  }, [])

  return (
    <div className="page-shell">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">LEARNING</div>
          <h1>Recommended next</h1>
        </div>
      </div>

      <div className="stack-list">
        {lessons.map((lesson) => (
          <div key={lesson.title} className="panel learning-item">
            <div className="learning-top">
              <span className="mini-icon"><BookOpen size={16} /></span>
              <div>
                <h3>{lesson.title}</h3>
                <p>{lesson.reason}</p>
              </div>
            </div>

            <div className="learning-meta">
              <span className="status-badge soft"><CheckCircle2 size={12} /> {lesson.status}</span>
              <span className="meta-chip"><Clock3 size={12} /> {lesson.duration}</span>
            </div>

            <button type="button" className="text-button">
              Explore <ArrowRight size={14} />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
