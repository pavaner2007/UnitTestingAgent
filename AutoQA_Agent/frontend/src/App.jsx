import { useState } from 'react'
import { analyzeRepository, downloadPdf } from './api/client'

import Sidebar from './components/Sidebar'
import HeroSection from './components/HeroSection'
import MetricCards from './components/MetricCards'
import AnalysisTimeline from './components/AnalysisTimeline'
import InsightsPanel from './components/InsightsPanel'
import TechStackPanel from './components/TechStackPanel'
import EvidenceAccordion from './components/EvidenceAccordion'
import ApiTable from './components/ApiTable'
import ArchitectureFlow from './components/ArchitectureFlow'
import HistoryPage from './pages/HistoryPage'

import './index.css'

export default function App() {
  const [page, setPage] = useState('home')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [report, setReport] = useState(null)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [historyCount, setHistoryCount] = useState(0)

  async function handleAnalyze(url) {
    setError('')
    setReport(null)
    setLoading(true)
    try {
      const data = await analyzeRepository(url)
      setReport(data.report)
      setHistoryCount(c => c + 1)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleDownloadPdf() {
    if (!report) return
    setPdfLoading(true)
    try {
      await downloadPdf(report.analysis_id, report.repository_name)
    } catch (err) {
      setError('PDF download failed: ' + err.message)
    } finally {
      setPdfLoading(false)
    }
  }

  function handleSelectReport(r) {
    setReport(r)
    setPage('home')
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sidebar
        activePage={page}
        onNavigate={setPage}
        historyCount={historyCount}
      />

      {/* Main content */}
      <main style={{ flex: 1, minWidth: 0, overflowY: 'auto', background: 'var(--bg-app)' }}>

        {/* ─── HISTORY PAGE ─── */}
        {page === 'history' && (
          <HistoryPage onSelectReport={handleSelectReport} />
        )}

        {/* ─── DASHBOARD PAGE ─── */}
        {page === 'home' && (
          <div style={{ padding: '40px 36px', maxWidth: 1120, margin: '0 auto' }}>

            {/* Hero / Input */}
            <HeroSection
              onAnalyze={handleAnalyze}
              loading={loading}
              error={error}
            />

            {/* Loading skeleton */}
            {loading && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginBottom: 24 }}>
                <div className="skeleton" style={{ height: 100 }} />
                <div className="skeleton" style={{ height: 64 }} />
                <div className="skeleton" style={{ height: 280 }} />
              </div>
            )}

            {/* ─── RESULTS ─── */}
            {report && !loading && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

                {/* Metric cards + PDF download */}
                <MetricCards
                  report={report}
                  onDownload={handleDownloadPdf}
                  pdfLoading={pdfLoading}
                />

                {/* Analysis steps timeline */}
                <AnalysisTimeline visible={!!report} />

                {/* AI Insights — tabbed panel */}
                {report.ai_explanation && (
                  <InsightsPanel
                    explanation={report.ai_explanation}
                    repoName={report.repository_name}
                    detectedFeatures={report.detected_features || []}
                    confidenceScore={report.confidence_score}
                    architectureNotes={report.architecture_notes}
                  />
                )}

                {/* Bottom two-column: Tech + Evidence */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
                  gap: 20,
                }}>
                  <TechStackPanel
                    stack={report.technology_stack}
                    architectureNotes={report.architecture_notes}
                  />
                  <EvidenceAccordion report={report} />
                </div>

                {/* API inventory table */}
                <ApiTable endpoints={report.api_inventory} />

                {/* Architecture flow diagram */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
                  gap: 20,
                }}>
                  <ArchitectureFlow report={report} />
                </div>

              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
