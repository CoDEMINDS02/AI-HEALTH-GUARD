import { Route, Routes } from 'react-router-dom'
import Header from './components/Header.jsx'
import DisclaimerBanner from './components/DisclaimerBanner.jsx'
import { FlowProvider } from './context/FlowContext.jsx'
import AnalyzingPage from './pages/AnalyzingPage.jsx'
import FollowUpPage from './pages/FollowUpPage.jsx'
import HistoryPage from './pages/HistoryPage.jsx'
import LandingPage from './pages/LandingPage.jsx'
import ProfilePage from './pages/ProfilePage.jsx'
import ReportPage from './pages/ReportPage.jsx'
import ResultsPage from './pages/ResultsPage.jsx'
import SymptomsPage from './pages/SymptomsPage.jsx'

export default function App() {
  return (
    <FlowProvider>
      <div className="app-shell">
        <Header />
        <DisclaimerBanner />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/symptoms" element={<SymptomsPage />} />
            <Route path="/follow-up" element={<FollowUpPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/analyze" element={<AnalyzingPage />} />
            <Route path="/results/:analysisId" element={<ResultsPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="*" element={<LandingPage />} />
          </Routes>
        </main>
        <footer className="footer">
          AI HealthGuard — educational prototype. It does not diagnose, prescribe, or replace a
          qualified healthcare professional. In an emergency, contact your local emergency number.
        </footer>
      </div>
    </FlowProvider>
  )
}
