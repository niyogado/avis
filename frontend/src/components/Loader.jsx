import React from 'react'
import {
  AlertCircle,
  Brain,
  Database,
  FileText,
  Loader2,
  Save,
  CheckCircle,
  Upload,
} from 'lucide-react'

const variantMap = {
  default: { icon: Loader2, title: 'Loading...' },
  ai: { icon: Brain, title: 'AVIS is thinking...' },
  cv: { icon: FileText, title: 'Analyzing your CV...' },
  upload: { icon: Upload, title: 'Uploading file...' },
  extracting: { icon: FileText, title: 'Extracting CV text...' },
  analyzing: { icon: Brain, title: 'Analyzing CV...' },
  save: { icon: Save, title: 'Saving changes...' },
  saving: { icon: Save, title: 'Saving analysis...' },
  success: { icon: CheckCircle, title: 'Complete' },
  fetch: { icon: Database, title: 'Fetching data...' },
  error: { icon: AlertCircle, title: 'Something went wrong' },
}

export default function Loader({
  variant = 'default',
  title,
  message,
  onRetry,
  retryLabel = 'Try again',
  compact = false,
}) {
  const config = variantMap[variant] || variantMap.default
  const Icon = config.icon
  const resolvedTitle = title || config.title
  const resolvedMessage = message || 'Please wait while AVIS completes the request.'

  return (
    <div className={`loader-shell ${compact ? 'compact' : ''} ${variant === 'error' ? 'error' : ''}`} role="status" aria-live="polite">
      <div className={`loader-icon ${variant === 'default' || variant === 'fetch' || variant === 'save' || variant === 'saving' || variant === 'upload' || variant === 'extracting' || variant === 'analyzing' || variant === 'cv' || variant === 'ai' ? 'spin' : ''}`}>
        <Icon size={18} />
      </div>

      <div className="loader-copy">
        <h3>{resolvedTitle}</h3>
        <p>{resolvedMessage}</p>
      </div>

      {variant === 'error' && onRetry && (
        <button type="button" className="secondary-button" onClick={onRetry}>
          {retryLabel}
        </button>
      )}
    </div>
  )
}
