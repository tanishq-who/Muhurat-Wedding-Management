import { useState } from 'react'

const SEASONS_DATA = [
  { folio: 'Singhania (IU)', date: '14 Feb 2027', couple: 'Aarav Singhania & Meera Kapoor', palace: 'Jagmandir Island & The Oberoi Udaivilas', circuit: 'Family • 600 Guests', gross: '₹4,20,00,000', vendor: '₹2,69,25,000', ops: '₹27,40,000', agencyNet: '₹1,24,39,000', margin: '29.6%', marginDir: 'up' },
  { folio: 'Piramal (LD)', date: '28 Jan 2027', couple: 'Kabir Joshi & Radhika Merchant', palace: 'Rambagh Palace & Jai Mahal', circuit: 'Hospitality • 480 Guests', gross: '₹2,65,00,000', vendor: '₹1,68,30,000', ops: '₹18,50,000', agencyNet: '₹78,20,000', margin: '29.5%', marginDir: 'up' },
  { folio: 'Mittal (JU)', date: '16 Jan 2027', couple: 'Aryan Mittal & Ameya Jindal', palace: 'The Leela Palace & Fateh Prakash', circuit: 'Conglomerate • 580 Guests', gross: '₹3,10,00,000', vendor: '₹1,93,50,000', ops: '₹24,00,000', agencyNet: '₹92,50,000', margin: '29.8%', marginDir: 'up' },
  { folio: 'Shah (UM)', date: '04 Dec 2026', couple: 'Aditya Piramal & Natasha Shah', palace: 'Umaid Palace & Mehrangarh Fort', circuit: 'Pharma Heir • 750 Guests', gross: '₹5,85,00,000', vendor: '₹3,58,00,000', ops: '₹32,00,000', agencyNet: '₹1,95,00,000', margin: '33.3%', marginDir: 'up' },
  { folio: 'Birla (JK)', date: '26 Nov 2026', couple: 'Rohan Oberoi & Rhea Birla', palace: 'Samode Palace & Haveli', circuit: 'Hospitality • 550 Guests', gross: '₹4,50,00,000', vendor: '₹3,15,00,000', ops: '₹25,60,000', agencyNet: '₹1,09,40,000', margin: '24.3%', marginDir: 'up' },
  { folio: 'Jaipuria (CT)', date: '12 Nov 2026', couple: 'Devendra Rula & Tanya Jaipuria', palace: 'Chhatra Sagar & Taj Lake Palace', circuit: 'Overall Flagged • 680 Guests', gross: '₹2,10,00,000', vendor: '₹1,72,30,000', ops: '₹14,28,000', agencyNet: '₹23,50,000', margin: '11.2%', marginDir: 'down', flag: true },
  { folio: 'Geenka (SS)', date: '24 Oct 2026', couple: 'Siddharth Geenka & Alisha Mehta', palace: 'Six Senses Fort Barwara', circuit: 'Private Equity • 380 Guests', gross: '₹1,45,00,000', vendor: '₹2,41,50,000', ops: '₹22,18,000', agencyNet: '₹81,40,000', margin: '23.6%', marginDir: 'up' },
]

const VENDORS_PERF = [
  { name: 'Rajwada Caterers', cat: 'Royal Mewar Shahi & Banquets', rating: '4.9', onTime: '96%', dispatch: '4.6', rating2: '★ 4.8 • 6 Weddings', trend: 'up', delta: '+6.0% (+₹72k)' },
  { name: 'Rathore Heritage Florals', cat: 'Mandap & Floral Architecture', rating: '4.2', onTime: '88%', dispatch: '4.6 (Queuing)', rating2: '★ 4.5 • 6 Weddings', trend: 'down', delta: '+9.4% (+₹1.3L)' },
  { name: 'SkyMagic Drone Pyrotechnics', cat: 'Lake Pichola Aerial Shows', rating: '5.0', onTime: '100%', dispatch: '4.8', rating2: '★ 5.0 • 3 Weddings', trend: 'neutral', delta: 'Exact (-0.8%)' },
  { name: 'Udaipur Royal Boat Ferries', cat: 'Lake Logistics & VIP Shikaras', rating: '4.7', onTime: '100%', dispatch: '4.9', rating2: '★ 4.9 • 6 Weddings', trend: 'neutral', delta: 'Exact (0.0%)' },
  { name: 'Sound & Acoustic Pro', cat: 'Jaipur Line Array & Rigging', rating: '4.3', onTime: '92%', dispatch: '3.8 (Queuing)', rating2: '★ 4.2 • 4 Weddings', trend: 'down', delta: '+7.2% (+₹45k)' },
  { name: 'House of Sabyasachi Valet', cat: 'Bridal Draping & Wardrobe Service', rating: '4.8', onTime: '100%', dispatch: '4.7 • Scheduled', rating2: '★ 4.8 • 4 Weddings', trend: 'up', delta: 'Exact (+2.1%)' },
]

const BAR_DATA = [
  { label: 'Singhania (IU)', net: 124, target: 90, pct: 29.6 },
  { label: 'Piramal (LD)', net: 110, target: 90, pct: 32.4 },
  { label: 'Oberoi (JP)', net: 95, target: 90, pct: 28.8 },
  { label: 'Mittal (JU)', net: 92, target: 90, pct: 29.8 },
  { label: 'Godrej (RT)', net: 64, target: 90, pct: 24.3, flag: true },
  { label: 'Merchant (LP)', net: 78, target: 90, pct: 21.3, flag: true },
  { label: 'Rua (UL)', net: 81, target: 90, pct: 27.5 },
  { label: 'Somani (1P)', net: 72, target: 90, pct: 25.0 },
]

const MAX_BAR = Math.max(...BAR_DATA.map(b => b.net))

export default function SeasonReview() {
  const [activeCircuit, setActiveCircuit] = useState('All (25)')

  return (
    <div className="page-canvas animate-fade-in">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span className="material-symbols-outlined">analytics</span>
        Founder Portfolio Audit • Confidential
      </div>

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Season Review — FY 2026-27 Executive Performance Dossier</h1>
          <p className="page-subtitle">Portfolio Financial Audits, Operating Margins &amp; Vendor Reliability Index (25 Heritage Celebrations across Udaipur, Jaipur, Jodhpur &amp; Ranthambore)</p>
        </div>
        <div className="page-actions">
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', border: '1px solid var(--beige-border)', borderRadius: 8, fontSize: 12, cursor: 'pointer' }}>
            Estate / City: All Circuits
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>expand_more</span>
          </div>
          <button className="btn-secondary" id="export-season-btn"><span className="material-symbols-outlined">download</span> Export Season Report (PDF/XLSX)</button>
          <button className="btn-primary" id="share-report-btn"><span className="material-symbols-outlined">share</span> Share Report</button>
        </div>
      </div>

      {/* Top KPIs */}
      <div className="grid-4 mb-4">
        <div className="kpi-card">
          <div className="kpi-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 13 }}>account_balance</span>
            Total Revenue (FY27)
          </div>
          <div className="kpi-value">₹68.45 Cr</div>
          <div style={{ fontSize: 12, color: 'var(--success)', fontWeight: 600, marginTop: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>trending_up</span>
            +18.4% vs FY26 &nbsp; Across 25 Celebrations
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 13 }}>savings</span>
            Net Agency Profit
          </div>
          <div className="kpi-value">₹14.82 Cr</div>
          <div className="kpi-sub" style={{ marginTop: 4 }}>Net retained fee margin pos…</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Blended Operating Margin</div>
          <div className="kpi-value">21.65%</div>
          <div style={{ fontSize: 11, color: 'var(--success)', fontWeight: 600, marginTop: 4 }}>
            <span className="badge badge-success" style={{ fontSize: 10 }}>Healthy Yield</span>
            <span style={{ marginLeft: 4, color: 'var(--on-surface-variant)' }}>+1.65% Over agency ceiling benchmark (20.0%)</span>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Dues in Next 30 Days</div>
          <div className="kpi-value">₹1.92 Cr</div>
          <div style={{ marginTop: 4, display: 'flex', gap: 6 }}>
            <span className="badge badge-danger" style={{ fontSize: 10 }}>2 Milestones Due</span>
          </div>
          <div className="kpi-sub" style={{ marginTop: 4 }}>5 upcoming milestone colle…</div>
        </div>
      </div>

      {/* Bar chart */}
      <div className="card mb-4">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>bar_chart</span>
            <span className="card-title">Profit Contribution &amp; Revenue Yield per Wedding</span>
          </div>
          <div style={{ display: 'flex', gap: 12, fontSize: 11 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 10, height: 10, background: 'var(--primary-container)', borderRadius: 2 }} /> Agency Net Profit (₹L)</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><div style={{ width: 10, height: 10, background: 'var(--secondary-container)', borderRadius: 2 }} /> Target Surplus Margin</span>
          </div>
        </div>
        <div className="card-body">
          <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginBottom: 20 }}>Net agency retained profit in Lakhs (₹L) across top benchmark celebrations throughout Rajasthan palace circuits</p>
          {/* Bar chart visualization */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end', height: 180, padding: '0 8px' }}>
            {BAR_DATA.map((b, i) => (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                {/* Target line indicator */}
                <div style={{ fontSize: 10, color: b.flag ? 'var(--danger)' : 'var(--on-surface-variant)', fontWeight: 600 }}>₹{b.net}L</div>
                <div style={{ width: '100%', position: 'relative', display: 'flex', justifyContent: 'center' }}>
                  <div style={{
                    width: '70%', height: `${(b.net / MAX_BAR) * 140}px`,
                    background: b.flag ? 'rgba(198,40,40,0.7)' : 'var(--primary-container)',
                    borderRadius: '3px 3px 0 0',
                    transition: 'height 0.4s',
                    minHeight: 4,
                  }} />
                </div>
                <div style={{ fontSize: 9, color: 'var(--on-surface-variant)', textAlign: 'center', lineHeight: 1.2 }}>{b.label}</div>
                <div style={{ fontSize: 9, color: b.flag ? 'var(--danger)' : 'var(--success)', fontWeight: 600 }}>{b.pct}%</div>
              </div>
            ))}
          </div>
          {/* Benchmark line label */}
          <div style={{ marginTop: 10, display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--on-surface-variant)' }}>
            <span>Key Insight: 19 of 25 celebrations exceeded the target 20% margin threshold. 3 celebrations exhibited supplier overrun compression below 15%.</span>
            <span style={{ color: 'var(--success)', fontWeight: 600, whiteSpace: 'nowrap' }}>Highest Yield: Mittal &amp; Jindal (29.8% margin)</span>
          </div>
        </div>
      </div>

      {/* Season ledger table */}
      <div className="card mb-4">
        <div className="card-header">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>table_rows</span>
              <span className="card-title">Master Season Ledger • 25 Royal Weddings</span>
            </div>
            <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginTop: 2 }}>Complete direct vendor disbursements, operating charges and agency gross margin</p>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            {['All (25)', 'Udaipur (8)', 'Jaipur (8)', 'Jodhpur (5)', 'Barwara (4)'].map(c => (
              <button key={c} className={`filter-tab${activeCircuit === c ? ' active' : ''}`} style={{ fontSize: 11, padding: '3px 10px' }} onClick={() => setActiveCircuit(c)}>{c}</button>
            ))}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date &amp; Folio</th>
                <th>Client &amp; Couple</th>
                <th>Palace Venue &amp; Circuit</th>
                <th>Gross Revenue</th>
                <th>Vendor Disbursal</th>
                <th>Ops / Crew</th>
                <th>Agency Net</th>
                <th>Margin %</th>
              </tr>
            </thead>
            <tbody>
              {SEASONS_DATA.map((row, i) => (
                <tr key={i}>
                  <td>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{row.date}</div>
                    <div style={{ fontSize: 10, color: 'var(--on-surface-variant)' }}>#{i + 845}</div>
                  </td>
                  <td>
                    <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 14, fontWeight: 700 }}>{row.couple}</div>
                  </td>
                  <td>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{row.palace}</div>
                    <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>{row.circuit}</div>
                  </td>
                  <td style={{ fontWeight: 700, fontSize: 14 }}>{row.gross}</td>
                  <td style={{ fontWeight: 600 }}>{row.vendor}</td>
                  <td style={{ fontWeight: 600 }}>{row.ops}</td>
                  <td style={{ fontWeight: 700, color: 'var(--success)' }}>{row.agencyNet}</td>
                  <td>
                    <span className={`badge badge-${row.flag ? 'danger' : row.marginDir === 'down' ? 'warning' : 'success'}`}>
                      {row.flag ? '⚠' : '↑'} {row.margin}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div style={{ padding: '12px 16px', borderTop: '1px solid var(--beige-border)', display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--on-surface-variant)' }}>
          <span>Displaying 1-19 of 25 Royal Celebrations &nbsp; <a href="#" style={{ color: 'var(--primary-container)' }}>Download Full 25-Record Audit Ledger (CSV)</a></span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>Previous</button>
            {[1, 2, 3].map(p => <button key={p} className={`filter-tab${p === 1 ? ' active' : ''}`} style={{ fontSize: 11, padding: '3px 9px' }}>{p}</button>)}
            <button className="btn-ghost" style={{ fontSize: 12, padding: '4px 10px' }}>Next</button>
          </div>
        </div>
      </div>

      {/* Bottom panels */}
      <div className="grid-2">
        {/* Vendor scorecard */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Heritage Vendor Scorecard</span>
            <span className="badge badge-gold" style={{ fontSize: 11 }}>6 Key Suppliers</span>
          </div>
          <div style={{ overflow: 'hidden' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>On-Time %</th>
                  <th>Dispatch</th>
                  <th>Rating</th>
                  <th>Cost Var.</th>
                </tr>
              </thead>
              <tbody>
                {VENDORS_PERF.map((v, i) => (
                  <tr key={i}>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: 12 }}>{v.name}</div>
                      <div style={{ fontSize: 10, color: 'var(--on-surface-variant)' }}>{v.cat}</div>
                    </td>
                    <td>
                      <div style={{ fontSize: 13, fontWeight: 700, color: parseFloat(v.onTime) >= 95 ? 'var(--success)' : 'var(--warning)' }}>{v.onTime}</div>
                    </td>
                    <td style={{ fontSize: 12 }}>{v.dispatch}</td>
                    <td style={{ fontSize: 12, color: 'var(--secondary)', fontWeight: 600 }}>{v.rating2}</td>
                    <td>
                      <span className={`badge badge-${v.trend === 'down' ? 'danger' : v.trend === 'neutral' ? 'success' : 'warning'}`} style={{ fontSize: 10 }}>{v.delta}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Escrow releases */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Upcoming Dues &amp; Escrow Releases</span>
            <span className="badge badge-warning" style={{ fontSize: 11 }}>5 Pending</span>
          </div>
          <div className="card-body">
            {[
              { folio: 'Singhania & Kapoor', desc: 'Final Settlement Balance • Client Receivable', due: 'Due in 6 days (22 Feb 2027)', amount: '₹47,69,000', action: 'Send Notice', type: 'warning' },
              { folio: 'Mittal & Jindal', desc: 'Tranche 02 Advance • Client Receivable', due: 'Due in 9 days (01 Mar 2027)', amount: '₹62,59,000', action: 'Auto-Invoice Active', type: 'neutral' },
              { folio: 'Piramal & Shah', desc: 'Escrow Release in Umaid Bhawan Palace • Client Receivable', due: 'Authorized disbursement date: 05 Nov 2027', amount: '₹45,29,000', action: 'Release Escrow', type: 'primary' },
              { folio: 'Goenka & Mehta', desc: 'Tranche 03 Advance • Vendor Receivable', due: 'Due in 18 days (04 Mar 2027)', amount: '₹37,09,000', action: 'Scheduled', type: 'neutral' },
            ].map((e, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', gap: 12, padding: '12px 0', borderBottom: i < 3 ? '1px solid var(--beige-border)' : 'none' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{e.folio} <span style={{ fontWeight: 400, fontSize: 11, color: 'var(--on-surface-variant)' }}>{e.desc}</span></div>
                  <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 2 }}>{e.due}</div>
                  <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, fontWeight: 700, color: 'var(--on-surface)', marginTop: 4 }}>{e.amount}</div>
                </div>
                <button className={`btn-${e.type === 'primary' ? 'primary' : e.type === 'warning' ? 'secondary' : 'ghost'}`} style={{ fontSize: 12, alignSelf: 'center', padding: '6px 12px', flexShrink: 0 }} id={`escrow-${i}-btn`}>
                  {e.action}
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
