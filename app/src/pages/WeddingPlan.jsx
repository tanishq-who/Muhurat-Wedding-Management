import { useState } from 'react'

const TASKS = {
  'To Plan': [
    { id: 1, tag: 'Reception', priority: 'Medium', title: 'Finalize Fireworks & Drone Light Show Permits', desc: 'Clearance needed from Udaipur Lake Police and Collectorate for mid-lake…', assignee: 'AS', name: 'Aryan Sharma', due: '28 Nov 2026' },
    { id: 2, tag: 'Wedding', priority: 'Normal', title: 'Royal Safa (Turban) & Dupatta Fabric Selection', desc: 'Select pure Kota Doria and Leheriya fabrics with Singhania royal crest…', assignee: 'DR', name: 'Devika Rao', due: '10 Dec 2026' },
    { id: 3, tag: 'Mehendi', priority: 'High', title: 'Curate Folk Artists & Manganiyar Troupe', desc: 'Contract Padam Shri awardee Manganiyar vocalists and Ghoomal...', assignee: 'PR', name: 'Pooja Rathore', due: '15 Dec 2026' },
  ],
  'In Progress': [
    { id: 4, tag: 'Venue', priority: 'Urgent', title: 'Jagmandir Lake Jetty Boat Transfer Logistics', desc: '14 covered luxury royal solar ferries scheduled between Udaivilas private…', assignee: 'RM', name: 'Rohan Mehta', due: '05 Nov 2026', progress: 60 },
    { id: 5, tag: 'Sangeet', priority: 'High', title: 'Sangeet Stage 3D Architectural Floral Mockup', desc: 'Rendering grand mirror-work arches and imported Dutch tuberose installations fo…', assignee: 'DR', name: 'Devika Rao', due: '18 Nov 2026', progress: 35 },
    { id: 6, tag: 'Vendors', priority: 'In Review', title: 'Sound & Acoustic Licensing for Pichola Shoreline', desc: 'Decibel zoning study and PPL / IPRS licensing submission for the midnight…', assignee: 'AS', name: 'Aryan Sharma', due: '25 Nov 2026', progress: 75 },
  ],
  'Done': [
    { id: 7, tag: 'Venue', priority: 'Completed', title: 'Palace Venue Lock & Royal Mandate Signed', desc: 'Full buyout agreements executed for Jagmandir Island Palace (14 Feb) and…', assignee: 'PR', name: 'Pooja Rathore', due: '18 Aug 2025', note: 'Signed by Pooja Rathore & General Manager' },
    { id: 8, tag: 'Vendors', priority: 'Completed', title: 'Catering RFP Selection: Rajwada Caterers Approved', desc: 'Four-day bespoke menu curated featuring authentic Mewari royal thalis,…', assignee: 'PR', name: 'Pooja Rathore', due: '02 Sep 2025', note: 'Menu tasting cleared with Singhania family' },
  ],
}

const PRIORITY_COLORS = {
  High: 'danger', Urgent: 'danger', 'In Review': 'warning', Medium: 'neutral', Normal: 'neutral', Completed: 'success',
}

const AVATAR_COLORS = {
  AS: '#7b1e3a', RM: '#2e7d5b', DR: '#795902', PR: '#322c1d',
}

export default function WeddingPlan() {
  return (
    <div className="page-canvas animate-fade-in">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span className="badge badge-neutral" style={{ fontSize: 11, marginRight: 4 }}>Udaipur Portfolio</span>
        <span className="material-symbols-outlined" style={{ fontSize: 13 }}>chevron_right</span>
        <span className="badge badge-neutral" style={{ fontSize: 11, marginRight: 4 }}>Jagmandir & Udaivilas</span>
        <span className="material-symbols-outlined" style={{ fontSize: 13 }}>chevron_right</span>
        <span className="badge badge-primary" style={{ fontSize: 11 }}>#WED-2027-0214</span>
      </div>

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Wedding Plan: Aarav Singhania &amp; Meera Kapoor</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>star</span>
            <span style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Heritage Multi-Estate Celebrations • Udaipur (Jagmandir Island Palace &amp; The Oberoi Udaivilas)</span>
          </div>
        </div>
        <div className="page-actions">
          <button className="btn-ghost" id="filter-tasks-btn"><span className="material-symbols-outlined">tune</span> Filter Tasks</button>
          <button className="btn-secondary" id="export-plan-btn"><span className="material-symbols-outlined">picture_as_pdf</span> Export Plan (PDF)</button>
          <button className="btn-primary" id="add-task-btn"><span className="material-symbols-outlined">add_circle</span> + Add Task</button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid-4 mb-4">
        <div className="kpi-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>brightness_5</span>
            <span className="kpi-label" style={{ marginBottom: 0 }}>Auspicious Countdown</span>
          </div>
          <div className="kpi-value">368 Days</div>
          <div className="kpi-sub">Target: 14 Feb 2027 (Basant Muhurat)</div>
        </div>
        <div className="kpi-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>groups</span>
            <span className="kpi-label" style={{ marginBottom: 0 }}>Guest Royal Manifest</span>
          </div>
          <div className="kpi-value">450 <span style={{ fontSize: 14, fontWeight: 500 }}>Confirmed</span></div>
          <div className="kpi-sub">180 VIP Suites Allocated</div>
        </div>
        <div className="kpi-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>account_balance_wallet</span>
            <span className="kpi-label" style={{ marginBottom: 0 }}>Fiscal Grand Total</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
            <div className="kpi-value">₹3.20 Cr</div>
            <span className="badge badge-warning" style={{ marginBottom: 4 }}>45% Allocated</span>
          </div>
          <div className="kpi-sub">Spent: ₹1.45 Cr</div>
          <div className="progress-bar mt-1"><div className="progress-fill" style={{ width: '45%' }} /></div>
        </div>
        <div className="kpi-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>flag</span>
            <span className="kpi-label" style={{ marginBottom: 0 }}>Milestone Stage</span>
          </div>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700 }}>Phase II Lock-in</div>
          <div className="kpi-sub">Decor &amp; Production Finalization</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--success)' }}>check_circle</span>
            <span style={{ fontSize: 11, color: 'var(--success)', fontWeight: 600 }}>On Track</span>
          </div>
        </div>
      </div>

      {/* Venue banner */}
      <div className="card mb-4" style={{ overflow: 'hidden' }}>
        <div style={{ display: 'flex', gap: 0, minHeight: 130 }}>
          <div style={{ flex: 1, padding: 16 }}>
            <span className="badge badge-primary mb-2">Venue Dispatch — Lake Pichola Heritage Circuit</span>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700, marginBottom: 6 }}>Dual Estate Island &amp; Courtyard Protocol</div>
            <p style={{ fontSize: 13, color: 'var(--on-surface-variant)', lineHeight: 1.55 }}>Mandap installation confirmed at Jagmandir Courtyard for Sunset Muhurat (17:45 IST). Udaivilas Promenade reserved for Royal Baraat assembly with 12 ceremonial Marwar...</p>
          </div>
          <div style={{ display: 'flex', gap: 2 }}>
            <img src="https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=200&h=140&fit=crop" alt="Jagmandir Island" style={{ width: 120, objectFit: 'cover' }} />
            <img src="https://images.unsplash.com/photo-1587474260584-136574528ed5?w=200&h=140&fit=crop" alt="Udaivilas" style={{ width: 120, objectFit: 'cover' }} />
          </div>
        </div>
      </div>

      {/* Payment milestones */}
      <div className="mb-6">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 18, verticalAlign: 'middle', marginRight: 6, color: 'var(--secondary)' }}>currency_rupee</span>
            Payment Milestones &amp; Escrow Tranches
          </h2>
          <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Standard Heritage Schedule (3-Tier)</span>
        </div>
        <div className="grid-3">
          {[
            { label: 'Tranche 01', title: 'Booking Advance / Royal Token', amount: '₹35,00,000', amountSub: '(₹35 Lakhs)', status: 'Paid', statusType: 'success', detail: 'Vault Receipt #VR-908 • Settled on 18 Aug 2025 • HDFC Royal Escrow', action: 'Cleared & Disbursed to Palaces' },
            { label: 'Tranche 02 (50%)', title: 'Advance Tranche (50%)', amount: '₹1,25,00,000', amountSub: '(₹1.25 Cr)', status: 'Due in 11 Mos', statusType: 'warning', detail: 'Due Date: 14 Jan 2027 • Decor mobilization, culinary advance & artist locks', action: 'Bank Guarantee Pending View Schedule' },
            { label: 'Tranche 03 (Balance)', title: 'Final Settlement', amount: '₹1,60,00,000', amountSub: '(₹1.60 Cr)', status: 'After Wedding', statusType: 'neutral', detail: 'Audit Date: 18 Feb 2027 • Final reconciliation & vendor disbursals', action: 'Post-Reception Audit  Pending Delivery' },
          ].map(t => (
            <div key={t.label} className="card">
              <div className="card-header">
                <span style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--on-surface-variant)' }}>{t.label}</span>
                <span className={`badge badge-${t.statusType}`}>{t.status}</span>
              </div>
              <div className="card-body">
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, marginBottom: 2 }}>{t.amount}</div>
                <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginBottom: 10 }}>{t.amountSub}</div>
                <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', lineHeight: 1.5, borderTop: '1px solid var(--beige-border)', paddingTop: 10, marginBottom: 10 }}>{t.detail}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: 'var(--primary-container)', fontWeight: 600 }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 13 }}>chevron_right</span>
                  {t.action}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Task Pipeline kanban */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 18, verticalAlign: 'middle', marginRight: 6, color: 'var(--secondary)' }}>task_alt</span>
          Operations &amp; Task Pipeline
        </h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Showing 8 Active Deliverables</span>
          <button className="btn-ghost" style={{ fontSize: 12 }} id="timeline-view-btn"><span className="material-symbols-outlined" style={{ fontSize: 14 }}>timeline</span> Timeline View</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 8 }}>
        {Object.entries(TASKS).map(([col, tasks]) => (
          <div key={col} style={{ minWidth: 280, flex: 1, maxWidth: 340 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: col === 'Done' ? 'var(--success)' : col === 'In Progress' ? 'var(--secondary)' : 'var(--warning)' }} />
                <span style={{ fontWeight: 700, fontSize: 15 }}>{col}</span>
                <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', background: 'var(--surface-container-high)', borderRadius: 9999, padding: '1px 7px' }}>{tasks.length}</span>
              </div>
              <button className="btn-ghost" style={{ padding: 4 }} id={`add-${col.replace(/ /g,'-').toLowerCase()}-task-btn`}>
                <span className="material-symbols-outlined" style={{ fontSize: 18 }}>add</span>
              </button>
            </div>
            {tasks.map(task => (
              <div key={task.id} className="pipeline-card" style={{ marginBottom: 10 }}>
                <div style={{ display: 'flex', gap: 6, marginBottom: 8, flexWrap: 'wrap' }}>
                  <span className="badge badge-neutral" style={{ fontSize: 10 }}>{task.tag}</span>
                  <span className={`badge badge-${PRIORITY_COLORS[task.priority] || 'neutral'}`} style={{ fontSize: 10 }}>
                    {task.priority === 'Urgent' && '⚠ '}{task.priority}
                  </span>
                </div>
                <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--on-surface)', marginBottom: 4, lineHeight: 1.3 }}>{task.title}</div>
                <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', lineHeight: 1.4, marginBottom: 10 }}>{task.desc}</p>
                {task.note && <div style={{ fontSize: 11, color: 'var(--success)', fontStyle: 'italic', marginBottom: 8 }}>✓ {task.note}</div>}
                {task.progress !== undefined && (
                  <div className="progress-bar mb-2"><div className="progress-fill" style={{ width: `${task.progress}%` }} /></div>
                )}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 22, height: 22, borderRadius: '50%', background: AVATAR_COLORS[task.assignee] || 'var(--primary-container)', color: 'white', fontSize: 9, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{task.assignee}</div>
                    <span style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>{task.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: 'var(--on-surface-variant)' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 12 }}>calendar_month</span>
                    {task.due}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
