import { useState, useRef } from 'react'
import {
  FileUp,
  FileText,
  CheckCircle2,
  AlertCircle,
  Copy,
  Check,
  X,
  Sparkles,
  Lock,
  Unlock,
  Eye,
  EyeOff,
} from 'lucide-react'
import PageHeader from '../components/layout/PageHeader.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import { previewPdfImport } from '../api.js'

function formatBytes(bytes) {
  if (!bytes || bytes <= 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

export default function ImportPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [infoNotice, setInfoNotice] = useState('')
  const [result, setResult] = useState(null)
  const [activePageIndex, setActivePageIndex] = useState(0)
  const [copied, setCopied] = useState(false)
  const fileInputRef = useRef(null)

  // Password-protected PDF state
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [password, setPassword] = useState('')
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [passwordError, setPasswordError] = useState('')
  const [submittingPassword, setSubmittingPassword] = useState(false)

  const activePage = result?.pages?.[activePageIndex] || null

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragover' || e.type === 'dragenter') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    const file = e.dataTransfer?.files?.[0]
    validateAndSetFile(file)
  }

  const handleFileInput = (e) => {
    const file = e.target.files?.[0]
    validateAndSetFile(file)
  }

  const validateAndSetFile = (file) => {
    if (!file) return
    setError('')
    setInfoNotice('')
    setResult(null)
    setActivePageIndex(0)
    setPassword('')
    setPasswordError('')
    setShowPasswordModal(false)

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF file (.pdf).')
      setSelectedFile(null)
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Selected file exceeds the 10 MB limit.')
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
  }

  const handleExtract = async () => {
    if (!selectedFile) return
    setLoading(true)
    setError('')
    setInfoNotice('')
    try {
      const data = await previewPdfImport(selectedFile)
      if (data.status === 'password_required') {
        setResult(data)
        setShowPasswordModal(true)
        setPassword('')
        setPasswordError('')
      } else {
        setResult(data)
        setActivePageIndex(0)
      }
    } catch (err) {
      const serverMsg =
        err.response?.data?.error ||
        (typeof err.response?.data?.detail === 'string' ? err.response?.data?.detail : null) ||
        'Failed to process the PDF statement. Check that the server is running.'
      setError(serverMsg)
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordSubmit = async (e) => {
    e.preventDefault()
    if (!selectedFile || !password.trim()) return

    setSubmittingPassword(true)
    setPasswordError('')
    try {
      const data = await previewPdfImport(selectedFile, password)
      setResult(data)
      setActivePageIndex(0)
      setError('')
      setInfoNotice('')
      setShowPasswordModal(false)
      // Immediately clear sensitive password from memory
      setPassword('')
      setPasswordVisible(false)
    } catch (err) {
      const errorData = err.response?.data
      const isIncorrectPassword =
        errorData?.code === 'incorrect_password' ||
        (typeof errorData?.error === 'string' && errorData.error.toLowerCase().includes('password'))

      if (isIncorrectPassword) {
        setPasswordError(errorData?.error || 'Incorrect password. Please verify and try again.')
      } else {
        const fallbackMsg = errorData?.error || 'Failed to decrypt document.'
        setPasswordError(fallbackMsg)
      }
    } finally {
      setSubmittingPassword(false)
    }
  }

  const handlePasswordCancel = () => {
    setShowPasswordModal(false)
    setPassword('')
    setPasswordError('')
    setPasswordVisible(false)
    setInfoNotice('Statement preview paused: Document password was not provided.')
  }

  const handleClear = () => {
    setSelectedFile(null)
    setResult(null)
    setError('')
    setInfoNotice('')
    setActivePageIndex(0)
    setPassword('')
    setPasswordError('')
    setShowPasswordModal(false)
    setPasswordVisible(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleCopy = () => {
    if (!activePage?.text) return
    navigator.clipboard.writeText(activePage.text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <>
      <PageHeader
        title="Statement Import"
        description="Upload a bank statement PDF to preview extracted text and page diagnostics without saving data."
      />

      {error ? <div className="notice error">{error}</div> : null}
      {infoNotice ? <div className="notice" style={{ background: '#1c1c1c', border: '1px solid #333', color: '#ccc' }}>{infoNotice}</div> : null}

      <div className="dashboard-grid">
        {/* Upload Card */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Upload PDF Statement</h2>
              <p>Supports digital text-based and password-protected PDF statements up to 10 MB.</p>
            </div>
            <span className="category-pill">Phase 1 Preview</span>
          </div>

          <div
            className={`dropzone ${dragActive ? 'active' : ''}`}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,application/pdf"
              style={{ display: 'none' }}
              onChange={handleFileInput}
            />
            <div className="dropzone-icon">
              {result?.status === 'password_required' ? (
                <Lock size={24} style={{ color: '#ffb347' }} />
              ) : result?.diagnostics?.is_encrypted ? (
                <Unlock size={24} style={{ color: 'var(--green)' }} />
              ) : (
                <FileUp size={24} />
              )}
            </div>
            <strong>
              {selectedFile ? selectedFile.name : 'Click or drop bank statement PDF'}
            </strong>
            <p>
              {selectedFile
                ? `${formatBytes(selectedFile.size)} selected`
                : 'Drag and drop your statement file here, or click to browse'}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
            {result?.status === 'password_required' ? (
              <button
                className="primary-button"
                onClick={() => setShowPasswordModal(true)}
                style={{ flex: 1, background: '#ffb347', color: '#1a1005', borderColor: '#ffb347' }}
              >
                <Lock size={15} /> Enter document password
              </button>
            ) : (
              <button
                className="primary-button"
                disabled={!selectedFile || loading}
                onClick={handleExtract}
                style={{ flex: 1 }}
              >
                <Sparkles size={16} />
                {loading ? 'Extracting text…' : 'Extract preview'}
              </button>
            )}
            {selectedFile ? (
              <button className="outline-button" onClick={handleClear} disabled={loading}>
                <X size={15} /> Clear
              </button>
            ) : null}
          </div>
        </section>

        {/* Diagnostics & Extraction Status */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Extraction Summary</h2>
              <p>Page counts, security status, and optical recognition diagnostics.</p>
            </div>
          </div>

          {result ? (
            <div style={{ display: 'grid', gap: '14px' }}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(3, 1fr)',
                  gap: '10px',
                }}
              >
                <div style={{ background: '#171717', border: '1px solid #282828', borderRadius: '12px', padding: '14px' }}>
                  <span style={{ fontSize: '11px', color: '#999', display: 'block' }}>TOTAL PAGES</span>
                  <strong style={{ fontSize: '20px', color: '#fff' }}>{result.total_pages}</strong>
                </div>
                <div style={{ background: '#171717', border: '1px solid #282828', borderRadius: '12px', padding: '14px' }}>
                  <span style={{ fontSize: '11px', color: '#999', display: 'block' }}>CHARACTERS</span>
                  <strong style={{ fontSize: '20px', color: '#fff' }}>{result.total_characters.toLocaleString()}</strong>
                </div>
                <div style={{ background: '#171717', border: '1px solid #282828', borderRadius: '12px', padding: '14px' }}>
                  <span style={{ fontSize: '11px', color: '#999', display: 'block' }}>WORDS</span>
                  <strong style={{ fontSize: '20px', color: '#fff' }}>{result.total_words.toLocaleString()}</strong>
                </div>
              </div>

              {result.status === 'password_required' ? (
                <div
                  style={{
                    background: '#2b2111',
                    border: '1px solid #6b4e18',
                    borderRadius: '12px',
                    padding: '14px',
                    color: '#ffc875',
                    display: 'flex',
                    gap: '12px',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <Lock size={19} style={{ flexShrink: 0 }} />
                    <span style={{ fontSize: '12px' }}>{result.message}</span>
                  </div>
                  <button
                    className="primary-button"
                    style={{ padding: '6px 12px', fontSize: '11px', background: '#ffb347', color: '#1a1005', borderColor: '#ffb347' }}
                    onClick={() => setShowPasswordModal(true)}
                  >
                    Unlock
                  </button>
                </div>
              ) : result.status === 'ocr_needed' ? (
                <div
                  style={{
                    background: '#281c10',
                    border: '1px solid #573919',
                    borderRadius: '12px',
                    padding: '14px',
                    color: '#ffc17d',
                    display: 'flex',
                    gap: '12px',
                    alignItems: 'flex-start',
                  }}
                >
                  <AlertCircle size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
                  <div style={{ fontSize: '12px', lineHeight: 1.5 }}>
                    <strong style={{ display: 'block', marginBottom: '3px' }}>Scanned / Image-Based PDF Detected</strong>
                    {result.message}
                  </div>
                </div>
              ) : (
                <div
                  style={{
                    background: '#122616',
                    border: '1px solid #24472b',
                    borderRadius: '12px',
                    padding: '14px',
                    color: '#9BE49B',
                    display: 'flex',
                    gap: '12px',
                    alignItems: 'center',
                  }}
                >
                  <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
                  <div style={{ fontSize: '12px' }}>
                    {result.message}
                    {result.diagnostics?.is_encrypted ? (
                      <span style={{ marginLeft: '8px', color: 'var(--green)', fontWeight: 600 }}>
                        (Decrypted with password)
                      </span>
                    ) : null}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="empty-state" style={{ minHeight: '160px' }}>
              <FileText size={28} />
              <span>Diagnostics will appear after extracting a statement</span>
            </div>
          )}
        </section>
      </div>

      {/* Extracted Text Content */}
      <article className="panel" style={{ marginTop: '16px' }}>
        <div className="panel-heading">
          <div>
            <h2>Extracted Text Preview</h2>
            <p>
              {result && activePage
                ? `Showing page ${activePage.page_number} of ${result.total_pages} (${activePage.character_count} characters, ${activePage.word_count} words)`
                : 'Raw text extracted from uploaded statement pages.'}
            </p>
          </div>
          {activePage?.text ? (
            <button className="outline-button" onClick={handleCopy}>
              {copied ? <Check size={14} className="positive" /> : <Copy size={14} />}
              {copied ? 'Copied' : 'Copy page text'}
            </button>
          ) : null}
        </div>

        {loading ? (
          <div className="empty-state">
            <Sparkles size={32} className="positive" />
            <strong>Extracting text from PDF…</strong>
            <span>Reading document layout and font encodings</span>
          </div>
        ) : result && result.status === 'password_required' ? (
          <div className="empty-state" style={{ minHeight: '180px' }}>
            <Lock size={32} style={{ color: '#ffb347' }} />
            <strong style={{ color: '#ffb347' }}>Document is password-protected</strong>
            <span>Enter the password to decrypt pages and inspect extracted text.</span>
            <button
              className="primary-button"
              style={{ marginTop: '10px', background: '#ffb347', color: '#1a1005', borderColor: '#ffb347' }}
              onClick={() => setShowPasswordModal(true)}
            >
              Enter Password
            </button>
          </div>
        ) : result && result.pages.length > 0 ? (
          <div>
            {result.pages.length > 1 ? (
              <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
                {result.pages.map((p, idx) => (
                  <button
                    key={p.page_number}
                    className={`page-pill ${activePageIndex === idx ? 'active' : ''}`}
                    onClick={() => setActivePageIndex(idx)}
                  >
                    Page {p.page_number}
                    {p.character_count > 0 ? ` (${p.character_count} chars)` : ' (empty)'}
                  </button>
                ))}
              </div>
            ) : null}

            {activePage?.error ? (
              <div className="notice error">{activePage.error}</div>
            ) : activePage?.text ? (
              <pre className="code-preview">{activePage.text}</pre>
            ) : (
              <div className="empty-state" style={{ minHeight: '180px' }}>
                <AlertCircle size={28} />
                <strong>No text found on this page</strong>
                <span>This page contains no extractable digital text stream.</span>
              </div>
            )}
          </div>
        ) : (
          <EmptyState
            icon={FileUp}
            title="No statement preview available"
            message="Upload a PDF above and click 'Extract preview' to inspect statement contents."
          />
        )}
      </article>

      {/* Password Modal */}
      {showPasswordModal ? (
        <div
          className="modal-backdrop"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget && !submittingPassword) {
              handlePasswordCancel()
            }
          }}
        >
          <form className="modal" onSubmit={handlePasswordSubmit}>
            <div className="modal-header">
              <div>
                <h2>Protected Statement</h2>
                <p>This statement requires a password to decrypt. Enter the password below.</p>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={handlePasswordCancel}
                disabled={submittingPassword}
                aria-label="Close dialog"
              >
                <X size={19} />
              </button>
            </div>

            {passwordError ? (
              <div className="notice error">{passwordError}</div>
            ) : null}

            <label>
              Password
              <div style={{ position: 'relative' }}>
                <input
                  type={passwordVisible ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    if (passwordError) setPasswordError('')
                  }}
                  placeholder="Enter PDF password"
                  autoFocus
                  required
                  autoComplete="off"
                  disabled={submittingPassword}
                  style={{ paddingRight: '42px' }}
                />
                <button
                  type="button"
                  className="icon-button"
                  onClick={() => setPasswordVisible((v) => !v)}
                  aria-label={passwordVisible ? 'Hide password' : 'Show password'}
                  style={{
                    position: 'absolute',
                    right: '10px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: '#888',
                  }}
                >
                  {passwordVisible ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </label>

            <div className="modal-actions">
              <button
                type="button"
                className="outline-button"
                onClick={handlePasswordCancel}
                disabled={submittingPassword}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="primary-button"
                disabled={!password.trim() || submittingPassword}
              >
                {submittingPassword ? 'Unlocking…' : 'Unlock & Preview'}
              </button>
            </div>
          </form>
        </div>
      ) : null}
    </>
  )
}
