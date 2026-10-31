import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Login from './pages/Login'
import Layout from './components/Layout'
import Enquiries from './pages/Enquiries'
import Quotes from './pages/Quotes'
import WeddingPlan from './pages/WeddingPlan'
import MuhuratTimeline from './pages/MuhuratTimeline'
import Agreements from './pages/Agreements'
import Settlement from './pages/Settlement'
import SeasonReview from './pages/SeasonReview'

function App() {
  const [loggedIn, setLoggedIn] = useState(false)

  if (!loggedIn) {
    return (
      <BrowserRouter>
        <Login onLogin={() => setLoggedIn(true)} />
      </BrowserRouter>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout onSignOut={() => setLoggedIn(false)} />}>
          <Route index element={<Navigate to="/enquiries" replace />} />
          <Route path="enquiries" element={<Enquiries />} />
          <Route path="agreements" element={<Agreements />} />
          <Route path="quotes" element={<Quotes />} />
          <Route path="wedding-plan" element={<WeddingPlan />} />
          <Route path="muhurat-timeline" element={<MuhuratTimeline />} />
          <Route path="settlement" element={<Settlement />} />
          <Route path="season-review" element={<SeasonReview />} />
        </Route>
        <Route path="*" element={<Navigate to="/enquiries" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
