import React, { useEffect, useMemo, useRef, useState } from 'react'
import {
  AlertCircle,
  Brain,
  Briefcase,
  CheckCircle,
  Code,
  FileText,
  GraduationCap,
  Target,
  Upload,
} from 'lucide-react'
import apiClient from '../api/config'
import Loader from '../components/Loader'
import ProfessionalIdentityEditor from '../components/ProfessionalIdentityEditor'

const PAGE_SIZE = 2600

const stageCopy = {
  uploading: ['upload', 'Uploading CV...', 'Sending the original file to AVIS.'],
  extracting: ['extracting', 'Extracting CV text...', 'The backend is reading the PDF or DOCX content.'],
  analyzing: ['analyzing', 'Analyzing CV...', 'Avis is extracting structured career evidence.'],
  saving: ['saving', 'Saving analysis...', 'AVIS is storing the validated CV memory.'],
  error: ['error', 'CV analysis failed', 'Retry the failed step when you are ready.'],
}

const formatDate = (value) => {
  if (!value) return 'Not analyzed yet'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}

const toList = (value) => (Array.isArray(value) ? value.filter(Boolean) : [])

const chunkText = (text) => {
  const clean = (text || '').trim()
  if (!clean) return []
  const chunks = []
  for (let index = 0; index < clean.length; index += PAGE_SIZE) {
    chunks.push(clean.slice(index, index + PAGE_SIZE))
  }
  return chunks
}

function Section({ icon: Icon, title, items, empty }) {
  return (
    <section className="cv-analysis-section">
      <div className="cv-section-title">
        <Icon size={16} />
        <strong>{title}</strong>
      </div>
      {items.length > 0 ? (
        <ul className="check-list">
          {items.map((item) => <li key={item}>{item}</li>)}
        </ul>
      ) : (
        <p className="cv-empty-copy">{empty}</p>
      )}
    </section>
  )
}

export default function MyCV() {
  const [cvs, setCvs] = useState([])
  const [activeCv, setActiveCv] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)
  const [filePreviewUrl, setFilePreviewUrl] = useState('')
  const [docxHtml, setDocxHtml] = useState('')
  const [previewKind, setPreviewKind] = useState('')
  const [pdfPageCount, setPdfPageCount] = useState(0)
  const [previewMode, setPreviewMode] = useState('file')
  const [pageIndex, setPageIndex] = useState(0)
  const [zoom, setZoom] = useState(100)
  const [stage, setStage] = useState('idle')
  const [error, setError] = useState('')
  const [intentDraft, setIntentDraft] = useState('')
  const [savingIntent, setSavingIntent] = useState(false)
  const fileInputRef = useRef(null)

  const busy = ['uploading', 'extracting', 'analyzing', 'saving'].includes(stage)
  const analysis = activeCv?.analysis_json || null
  const evidence = analysis?.cv_evidence || {}
  const interpretation = analysis?.ai_interpretation || {}
  const previewText = activeCv?.extracted_text || ''
  const pages = useMemo(() => chunkText(previewText), [previewText])
  const currentPage = pages[Math.min(pageIndex, Math.max(pages.length - 1, 0))] || ''
  const canShowFilePreview = Boolean(filePreviewUrl || docxHtml)
  const pdfSrc = filePreviewUrl
    ? `${filePreviewUrl}#page=${pageIndex + 1}&zoom=${zoom}`
    : ''

  const latestCv = cvs[0] || null

  const revokePreviewUrl = () => {
    if (filePreviewUrl) URL.revokeObjectURL(filePreviewUrl)
  }

  const loadSavedPreview = async (cv) => {
    if (!cv?.id) {
      setDocxHtml('')
      setPreviewKind('')
      setPdfPageCount(0)
      return
    }
    try {
      const preview = await apiClient.get(`/api/cv/${cv.id}/preview`)
      if (preview.data?.format === 'pdf') {
        const file = await apiClient.get(`/api/cv/${cv.id}/file`, { responseType: 'blob' })
        const url = URL.createObjectURL(file.data)
        setFilePreviewUrl((current) => {
          if (current) URL.revokeObjectURL(current)
          return url
        })
        setDocxHtml('')
        setPreviewKind('pdf')
        setPdfPageCount(preview.data.page_count || 0)
        setPreviewMode('file')
        return
      }
      if (preview.data?.format === 'docx') {
        setFilePreviewUrl((current) => {
          if (current) URL.revokeObjectURL(current)
          return ''
        })
        setDocxHtml(preview.data.html || '')
        setPreviewKind('docx')
        setPdfPageCount(1)
        setPreviewMode('file')
      }
    } catch (_) {
      setPreviewKind('')
    }
  }

  const loadCvs = async () => {
    try {
      const response = await apiClient.get('/api/cv/')
      const next = response.data || []
      setCvs(next)
      setActiveCv(next[0] || null)
      setIntentDraft(next[0]?.analysis_json?.career_intent?.current_intent || '')
      setError(next[0]?.analysis_status === 'error' ? next[0]?.analysis_error || 'The last analysis failed.' : '')
      await loadSavedPreview(next[0])
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load your saved CV.')
      setStage('error')
    }
  }

  useEffect(() => {
    loadCvs()
    return revokePreviewUrl
  }, [])

  useEffect(() => {
    setPageIndex(0)
    setIntentDraft(activeCv?.analysis_json?.career_intent?.current_intent || '')
  }, [activeCv?.id])

  useEffect(() => {
    if (!selectedFile) return undefined
    if (selectedFile.type === 'application/pdf' || selectedFile.name.toLowerCase().endsWith('.pdf')) {
      const url = URL.createObjectURL(selectedFile)
      setFilePreviewUrl((current) => {
        if (current) URL.revokeObjectURL(current)
        return url
      })
      setDocxHtml('')
      setPreviewKind('pdf')
      setPreviewMode('file')
      return () => URL.revokeObjectURL(url)
    }
    return undefined
  }, [selectedFile])

  const analyzeCv = async (cvId) => {
    setError('')
    setStage('analyzing')
    try {
      const response = await apiClient.post(`/api/cv/${cvId}/analyze`, new FormData(), {
        timeout: 90000,
      })
      setStage('saving')
      setActiveCv(response.data)
      setCvs((current) => [response.data, ...current.filter((cv) => cv.id !== response.data.id)])
      setStage('idle')
    } catch (err) {
      setError(err.response?.data?.detail || 'CV analysis could not be completed.')
      setStage('error')
    }
  }

  const uploadAndAnalyze = async (file) => {
    const form = new FormData()
    form.append('file', file)
    setSelectedFile(file)
    setError('')
    setStage('uploading')

    try {
      const uploadResponse = await apiClient.post('/api/cv/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
        onUploadProgress: (event) => {
          if (event.total && event.loaded >= event.total) {
            setStage('extracting')
          }
        },
      })
      setActiveCv(uploadResponse.data)
      setCvs((current) => [uploadResponse.data, ...current.filter((cv) => cv.id !== uploadResponse.data.id)])
      await loadSavedPreview(uploadResponse.data)
      await analyzeCv(uploadResponse.data.id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to upload or extract this CV.')
      setStage('error')
    }
  }

  const handleUploadInput = (event) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file || busy) return
    uploadAndAnalyze(file)
  }

  const retry = () => {
    if (selectedFile && (!activeCv || activeCv.analysis_status !== 'error')) {
      uploadAndAnalyze(selectedFile)
      return
    }
    if (activeCv?.id || latestCv?.id) {
      analyzeCv(activeCv?.id || latestCv.id)
    }
  }

  const saveIntent = async (value) => {
    if (!activeCv?.id || !value.trim() || savingIntent) return
    setSavingIntent(true)
    setError('')
    try {
      const response = await apiClient.post(`/api/cv/${activeCv.id}/intent`, {
        current_intent: value.trim(),
      })
      setActiveCv(response.data)
      setIntentDraft(value.trim())
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to save your career intent.')
    } finally {
      setSavingIntent(false)
    }
  }

  const [loaderVariant, loaderTitle, loaderMessage] = stageCopy[stage] || []

  const skills = toList(evidence.skills)
  const experience = toList(evidence.experience)
  const education = toList(evidence.education)
  const projects = toList(evidence.projects)
  const certifications = toList(evidence.certifications)
  const achievements = toList(evidence.achievements)
  const evidenceSignals = toList(evidence.career_signals)
  const strengths = toList(interpretation.strengths)
  const gaps = toList(interpretation.gaps)
  const interpretedSignals = toList(interpretation.career_signals)
  const directions = toList(interpretation.career_directions)
  const insights = toList(interpretation.insights || evidence.insights)
  const confirmedIntent = analysis?.career_intent?.current_intent || ''
  const textPageCount = pages.length
  const filePageCount = previewKind === 'pdf' ? pdfPageCount : 1
  const controlCount = previewMode === 'file' ? filePageCount : textPageCount

  return (
    <div className="page-shell cv-page">
      <div className="section-head narrow">
        <div>
          <div className="eyebrow">CV</div>
          <h1>CV Analyzer</h1>
        </div>

        <button type="button" className="primary-button" onClick={() => fileInputRef.current?.click()} disabled={busy}>
          <span className="button-content"><Upload size={14} />{activeCv ? 'Replace CV' : 'Upload CV'}</span>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleUploadInput}
          disabled={busy}
          style={{ display: 'none' }}
        />
      </div>

      {stage !== 'idle' && (
        <Loader
          variant={loaderVariant}
          title={loaderTitle}
          message={stage === 'error' ? error || loaderMessage : loaderMessage}
          onRetry={stage === 'error' ? retry : undefined}
          retryLabel="Retry"
        />
      )}

      <div className="cv-analyzer-grid">
        <section className="panel cv-preview-panel">
          <div className="cv-panel-head">
            <div className="title-line">
              <span className="mini-icon"><FileText size={16} /></span>
              <div>
                <strong>{activeCv?.filename || 'No CV uploaded'}</strong>
                <small>{activeCv ? `Uploaded ${formatDate(activeCv.created_at)}` : 'PDF or DOCX supported'}</small>
              </div>
            </div>
            <span className="status-badge">
              {analysis ? <CheckCircle size={12} /> : <FileText size={12} />}
              {analysis ? 'Analyzed' : 'Preview'}
            </span>
          </div>

          <div className="cv-preview-toolbar">
            <button type="button" className={previewMode === 'file' ? 'inline-button active' : 'inline-button'} onClick={() => setPreviewMode('file')} disabled={!canShowFilePreview}>
              File
            </button>
            <button type="button" className={previewMode === 'text' ? 'inline-button active' : 'inline-button'} onClick={() => setPreviewMode('text')} disabled={!previewText}>
              Extracted text
            </button>
            <button type="button" className="inline-button" onClick={() => setZoom((value) => Math.max(80, value - 10))} disabled={zoom <= 80}>
              -
            </button>
            <span className="cv-toolbar-value">{zoom}%</span>
            <button type="button" className="inline-button" onClick={() => setZoom((value) => Math.min(160, value + 10))} disabled={zoom >= 160}>
              +
            </button>
          </div>

          <div className="cv-preview-body">
            {previewMode === 'file' && previewKind === 'pdf' && pdfSrc ? (
              <iframe title="Uploaded CV preview" src={pdfSrc} className="cv-file-frame" />
            ) : previewMode === 'file' && previewKind === 'docx' && docxHtml ? (
              <iframe title="Uploaded DOCX preview" srcDoc={docxHtml} className="cv-file-frame" style={{ zoom: `${zoom}%` }} />
            ) : currentPage ? (
              <pre className="cv-text-preview" style={{ fontSize: `${zoom}%` }}>{currentPage}</pre>
            ) : (
              <div className="cv-empty-state">
                <FileText size={24} />
                <p>Upload a PDF or DOCX to preview the original document and extract its text.</p>
              </div>
            )}
          </div>

          <div className="cv-page-controls">
            <button type="button" className="secondary-button" onClick={() => setPageIndex((value) => Math.max(0, value - 1))} disabled={pageIndex === 0 || controlCount <= 1}>
              Previous
            </button>
            <span>Page {controlCount ? pageIndex + 1 : 0} of {controlCount || 0}</span>
            <button type="button" className="secondary-button" onClick={() => setPageIndex((value) => Math.min(controlCount - 1, value + 1))} disabled={pageIndex >= controlCount - 1 || controlCount <= 1}>
              Next
            </button>
          </div>
        </section>

        <section className="panel cv-analysis-panel">
          <div className="cv-panel-head">
            <div className="title-line">
              <span className="mini-icon"><Brain size={16} /></span>
              <div>
                <strong>AI Analysis</strong>
                <small>{activeCv?.analyzed_at ? `Saved ${formatDate(activeCv.analyzed_at)}` : 'Awaiting Avis analysis'}</small>
              </div>
            </div>
            {activeCv?.id && (
              <button type="button" className="secondary-button" onClick={() => analyzeCv(activeCv.id)} disabled={busy || !previewText}>
                Retry
              </button>
            )}
          </div>

          {analysis ? (
            <div className="cv-analysis-content">
              <section className="cv-profile-block">
                <div className="cv-section-title"><Briefcase size={16} /><strong>Professional Profile</strong></div>
                <p>{evidence.professional_profile || 'No professional profile was extracted.'}</p>
              </section>

              <div className="cv-evidence-band">
                <span>CV Evidence</span>
                <small>Facts directly present in the uploaded document.</small>
              </div>

              <Section icon={Code} title="Skills" items={skills} empty="No skills were extracted from the CV." />
              <Section icon={Briefcase} title="Experience" items={experience} empty="No experience section was extracted." />
              <Section icon={GraduationCap} title="Education" items={education} empty="No education section was extracted." />
              <Section icon={Target} title="Projects" items={projects} empty="No project evidence was extracted." />
              <Section icon={CheckCircle} title="Certifications" items={certifications} empty="No certifications were extracted." />
              <Section icon={CheckCircle} title="Achievements" items={achievements} empty="No achievements were extracted." />
              <Section icon={Briefcase} title="Career Signals" items={evidenceSignals} empty="No explicit career signals were present in the CV." />

              <div className="cv-interpretation-band">
                <span>AI Interpretation</span>
                <small>Inferred possibilities, not confirmed user choices.</small>
              </div>

              <Section icon={CheckCircle} title="Strengths" items={strengths} empty="No strengths were inferred." />
              <Section icon={AlertCircle} title="Gaps" items={gaps} empty="No gaps were inferred." />
              <Section icon={Target} title="Career Direction" items={directions} empty="No career directions were inferred." />
              <Section icon={Brain} title="AI Insights" items={insights.length ? insights : interpretedSignals} empty="No additional AI signals were inferred." />

              <section className="cv-profile-block">
                <div className="cv-section-title"><Target size={16} /><strong>Your career intent</strong></div>
                <p>{confirmedIntent || 'Not confirmed yet. AVIS will not treat inferred directions as your choice until you confirm.'}</p>
                {directions.length > 0 && !confirmedIntent && (
                  <div className="quick-actions" style={{ marginTop: 12 }}>
                    {directions.slice(0, 3).map((direction) => (
                      <button key={direction} type="button" className="secondary-button" onClick={() => saveIntent(direction)} disabled={savingIntent}>
                        {direction}
                      </button>
                    ))}
                  </div>
                )}
                <div className="quick-actions" style={{ marginTop: 12 }}>
                  <input
                    value={intentDraft}
                    onChange={(event) => setIntentDraft(event.target.value)}
                    placeholder="Confirm the direction you want now"
                    style={{ flex: 1, minWidth: 180, borderRadius: 12, border: '1px solid var(--border)', padding: '10px 12px', background: 'rgba(255,255,255,0.4)', color: 'var(--text)' }}
                  />
                  <button type="button" className="primary-button" onClick={() => saveIntent(intentDraft)} disabled={savingIntent || !intentDraft.trim()}>
                    {savingIntent ? 'Saving…' : 'Confirm intent'}
                  </button>
                </div>
              </section>

              <ProfessionalIdentityEditor analysis={analysis} />
            </div>
          ) : (
            <div className="cv-empty-state">
              <Brain size={24} />
              <p>{activeCv ? 'Run analysis to extract structured CV evidence and AI interpretation.' : 'Upload a CV to start the real AVIS pipeline.'}</p>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
