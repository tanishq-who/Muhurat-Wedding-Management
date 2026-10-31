import { useState } from 'react'

const ENQUIRIES = {
  'New Inquiries': [
    {
      id: 1, status: 'Astrology Matched', statusType: 'success', time: '2h ago',
      couple: 'Aarav Singhania & Meera Kapoor', venue: 'Royal Udaipur Palace (City Palace)',
      venueTag: 'Lake Pichola',
      image: 'https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=400&h=100&fit=crop',
      date: '14 Dec 2025', guests: '450 Guests', budget: '₹2.8 Cr', action: 'View',
    },
    {
      id: 2, status: 'Fresh Inquiry', statusType: 'neutral', time: '5h ago',
      couple: 'Devansh Rathore & Ananya Birla', venue: 'Rambagh Heritage Extravaganza (Jaipur)',
      image: null, venueTag: null,
      date: '18 Jan 2026', guests: '600 Guests', budget: '₹4.2 Cr', action: 'View',
    },
  ],
  'Consultation': [
    {
      id: 3, status: 'Meeting Set', statusType: 'warning', time: 'Tomorrow',
      couple: 'Vikramaditya Oberoi & Tara Sen', venue: 'Jagmandir Island Royal Twilight',
      badge2: 'Tasting & Decor Consult — Tomorrow at 3:00 PM IST (Jaipur HQ)',
      image: null, venueTag: null,
      date: '28 Nov 2025', guests: '350 Guests', budget: '₹3.5 Cr', action: 'Notes',
    },
    {
      id: 4, status: 'Virtual Consult', statusType: 'neutral', time: 'Thu 11 AM',
      couple: 'Kabir Joshi & Radhika Merchant', venue: 'Samode Palace Rajasthani Regalia',
      image: null, venueTag: null,
      date: '04 Feb 2026', guests: '500 Guests', budget: '₹2.1 Cr', action: 'Prep',
    },
  ],
  'Agreement': [
    {
      id: 5, status: 'Contract Sent', statusType: 'warning', time: 'v2.1 Draft',
      couple: 'Rohan Chawla & Samaira Khaitan', venue: 'Umaid Bhawan Royal Grandeur',
      venueTag: 'Jodhpur Heritage',
      image: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=400&h=100&fit=crop',
      date: '12 Nov 2025', guests: '750 Guests', budget: '₹5.5 Cr', action: 'Contract',
    },
    {
      id: 6, status: 'Reviewing Terms', statusType: 'neutral', time: 'Day 3',
      couple: 'Arjun Varma & Diya Parekh', venue: 'Fairmont Amber Fort Vista',
      image: null, venueTag: null,
      date: '22 Dec 2025', guests: '400 Guests', budget: '₹1.9 Cr', action: 'Revise',
    },
  ],
  'Confirmed': [
    {
      id: 7, status: 'Advance Received', statusType: 'success', time: 'Locked',
      couple: 'Yashvardhan Kothari & Sanjana Seth', venue: 'Leela Palace Lake Pichola Extravaganza',
      tokenNote: 'Token Advance: ₹1.5 Cr',
      image: null, venueTag: null,
      date: '08 Nov 2025', guests: '650 Guests', budget: '₹6.0 Cr', action: 'Manage',
    },
    {
      id: 8, status: 'Confirmed', statusType: 'success', time: 'Folio #842',
      couple: 'Nikhil Goenka & Tanvi Mehta', venue: 'Chomu Palace Regal Sangeet',
      image: null, venueTag: null,
      date: '19 Jan 2026', guests: '420 Guests', budget: '₹2.4 Cr', action: 'Manage',
    },
  ],
}

const COL_DOT_COLORS = {
  'New Inquiries': '#e0a100',
  'Consultation': '#795902',
  'Agreement': '#c62828',
  'Confirmed': '#2e7d5b',
}

const FILTERS = ['All Venues (28)', 'Jaipur Palaces (14)', 'Udaipur Lakefront (9)', 'High Value >₹3 Cr (8)', 'Astrology Verified (18)']

export default function Enquiries() {
  const [activeFilter, setActiveFilter] = useState(0)

  return (
    <div className="page-canvas animate-fade-in">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span className="material-symbols-outlined">manage_accounts</span>
        Client Intake &amp; Astrological Folios
      </div>

      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Enquiries</h1>
          <p className="page-subtitle">Manage royal client inquiries, astrological dates, and consultation pipelines across Jaipur and Udaipur heritage estates.</p>
        </div>
        <div className="page-actions">
          <button className="btn-primary" id="add-enquiry-btn">
            <span className="material-symbols-outlined">add_circle</span>
            + Add Enquiry
          </button>
          <button className="btn-secondary" id="export-folios-btn">
            <span className="material-symbols-outlined">download</span>
            Export Folios
          </button>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid-3 mb-4">
        <div className="kpi-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-label">Active Inquiries</div>
            <div className="kpi-value">28</div>
            <div className="kpi-sub" style={{ color: 'var(--success)' }}>+4 received this week</div>
          </div>
          <div className="kpi-icon"><span className="material-symbols-outlined">folder_open</span></div>
        </div>
        <div className="kpi-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-label">Pipeline Valuation</div>
            <div className="kpi-value">₹38.4 Cr</div>
            <div className="kpi-sub">Avg ₹2.7 Cr / celebration</div>
          </div>
          <div className="kpi-icon"><span className="material-symbols-outlined">currency_rupee</span></div>
        </div>
        <div className="kpi-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div className="kpi-label">Upcoming Muhurats</div>
            <div className="kpi-value">14 Bookings</div>
            <div className="kpi-sub">High astrological affinity</div>
          </div>
          <div className="kpi-icon"><span className="material-symbols-outlined">brightness_5</span></div>
        </div>
      </div>

      {/* Tithi Intelligence banner */}
      <div style={{ marginBottom: 20, background: 'var(--primary-container)', borderRadius: 10, padding: '14px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--secondary-fixed-dim)', marginBottom: 4 }}>Tithi Intelligence</div>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 16, fontWeight: 700, color: 'white' }}>Pushya Nakshatra Approaching</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.75)', marginTop: 2 }}>Peak demand for Lake Pichola venues</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--secondary-container)' }}>Surge Factor: 1.25x</span>
          <span className="material-symbols-outlined" style={{ color: 'var(--secondary-container)', fontSize: 18 }}>auto_awesome</span>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
        <div className="filter-tabs">
          {FILTERS.map((f, i) => (
            <button key={f} className={`filter-tab${activeFilter === i ? ' active' : ''}`} onClick={() => setActiveFilter(i)}>{f}</button>
          ))}
        </div>
        <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'flex', alignItems: 'center', gap: 4 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>swap_vert</span>
          Sorted by Auspicious Date Priority
        </div>
      </div>

      {/* Kanban Pipeline */}
      <div style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 8 }}>
        {Object.entries(ENQUIRIES).map(([colTitle, cards]) => (
          <div key={colTitle} className="pipeline-column">
            <div className="pipeline-col-header">
              <div className="pipeline-col-title">
                <div className="pipeline-dot" style={{ background: COL_DOT_COLORS[colTitle] }} />
                {colTitle}
              </div>
              <span className="pipeline-col-count">{cards.length}</span>
            </div>
            {cards.map(card => (
              <div key={card.id} className="pipeline-card">
                {/* Status row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className={`badge badge-${card.statusType}`}>{card.status}</span>
                  <span style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>{card.time}</span>
                </div>
                {/* Title */}
                <div className="pipeline-card-title">{card.couple}</div>
                {/* Venue */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--on-surface-variant)', marginBottom: 8 }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 13 }}>location_on</span>
                  {card.venue}
                </div>
                {/* Optional secondary badge */}
                {card.badge2 && (
                  <div style={{ fontSize: 11, background: 'var(--surface-container-low)', borderRadius: 6, padding: '6px 8px', color: 'var(--on-surface-variant)', marginBottom: 8, lineHeight: 1.4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 12, verticalAlign: 'middle', marginRight: 4 }}>calendar_month</span>
                    {card.badge2}
                  </div>
                )}
                {/* Token note */}
                {card.tokenNote && (
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }} className="badge badge-gold mb-2">{card.tokenNote}
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>verified</span>
                  </div>
                )}
                {/* Venue image */}
                {card.image && (
                  <div className="img-overlay mb-2">
                    <img src={card.image} alt={card.venue} className="card-venue-img" />
                    {card.venueTag && <span className="img-overlay-label">{card.venueTag}</span>}
                  </div>
                )}
                {/* Meta row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <div>
                    <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Date</div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface)' }}>{card.date}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Est. Guests</div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface)' }}>{card.guests}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Budget Folio</div>
                    <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, fontWeight: 700, color: 'var(--on-surface)' }}>{card.budget}</div>
                  </div>
                  <button className="btn-ghost" style={{ fontSize: 12, padding: '5px 10px' }}>
                    {card.action} <span className="material-symbols-outlined" style={{ fontSize: 14 }}>chevron_right</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
