import { useState } from 'react'

const MILESTONES = [
  { label: 'Token Advance & Royal Mandate Booking', date: '18 Aug 2025', status: 'Received', type: 'success', amount: '₹3,50,000', desc: 'Locking dates & Jagmandir reservation deposit' },
  { label: 'Stage 2: Sangeet & Decor Finalization', date: '30 Oct 2025', status: 'Scheduled', type: 'neutral', amount: '₹7,50,000', desc: 'Floral architecture & palace light engineering approval' },
  { label: 'Final Settlement & Royal Dispatch', date: '15 Nov 2025', status: 'Due Close', type: 'warning', amount: '₹7,50,000', desc: 'Comprehensive vendor close-out & concierge wrap' },
]

export default function Agreements() {
  const [signed, setSigned] = useState(false)
  const [checked, setChecked] = useState(false)

  return (
    <div className="page-canvas animate-fade-in">
      {/* Official header banner */}
      <div style={{ background: 'var(--surface-container-lowest)', border: '1px solid var(--beige-border)', borderRadius: 8, padding: '10px 16px', marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>verified</span>
          <span style={{ fontWeight: 600, color: 'var(--secondary)' }}>Official Heritage Wedding Services Contract — Legally Binding Under Rajasthan Solemnization &amp; Event Governance</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>key</span>
          <span style={{ color: 'var(--on-surface-variant)' }}>HASH: SHA256-RAJ-884-2025</span>
        </div>
      </div>

      {/* Folio ID */}
      <div className="breadcrumb">
        <span className="material-symbols-outlined">description</span>
        FOLIO #AGR-2025-884
        <span className="material-symbols-outlined" style={{ fontSize: 13 }}>circle</span>
        Palace Registry: Udaipur Div. IV
      </div>

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title" style={{ fontSize: 36 }}>Service Agreement &amp; Contract Execution</h1>
          <p className="page-subtitle">Aarav Singhania &amp; Meera Kapoor — Royal Udaipur Multi-Estate Celebrations</p>
        </div>
        <div className="page-actions">
          {['Pending Execution', 'Signed & Verified State'].map((label, i) => (
            <button
              key={label}
              style={{
                padding: '8px 16px', borderRadius: 8, border: '1px solid var(--beige-border)',
                background: i === 0 ? 'var(--warning-bg)' : 'var(--surface-container-lowest)',
                color: i === 0 ? 'var(--warning)' : 'var(--on-surface-variant)',
                fontWeight: 600, fontSize: 13, cursor: 'pointer', fontFamily: "'Inter', sans-serif",
              }}
              id={`agreement-tab-${i}-btn`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Status chips */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginBottom: 16 }}>
        <span className="badge badge-warning">
          <span className="material-symbols-outlined" style={{ fontSize: 12 }}>hourglass_top</span>
          Pending Client Signoff
        </span>
        <div style={{ fontSize: 13, color: 'var(--on-surface-variant)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 14 }}>security</span>
          Authentication Server — E-Sign Certified via Muhurat Vault • IP: 103.21.58.12 (Jaipur HQ)
        </div>
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 24, flexWrap: 'wrap' }}>
        <button className="btn-ghost" id="print-draft-btn"><span className="material-symbols-outlined">print</span> Print Draft</button>
        <button className="btn-primary" id="download-signed-pdf-btn">
          <span className="material-symbols-outlined">download</span>
          Download Signed PDF <span style={{ marginLeft: 6, fontSize: 11, background: 'rgba(255,255,255,0.2)', borderRadius: 9999, padding: '1px 6px' }}>4.2 MB</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 20, alignItems: 'start' }}>
        {/* Main contract */}
        <div>
          {/* Agreement card */}
          <div style={{ background: 'var(--primary-container)', borderRadius: 10, padding: 20, marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 12 }}>
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--secondary-fixed-dim)', marginBottom: 6 }}>The Royal Knot • Palace Registry</div>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: 'white', lineHeight: 1.2 }}>Royal Heritage Wedding Agreement</div>
              </div>
              <div style={{ textAlign: 'right', color: 'rgba(255,255,255,0.8)', fontSize: 12 }}>
                <div>Format AGR-2025-V3</div>
                <div>Valid Until 15 Nov 2025</div>
              </div>
            </div>
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'rgba(201,162,75,0.2)', border: '2px solid var(--gold)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: 12 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 20, color: 'var(--gold)' }}>shield</span>
            </div>
          </div>

          {/* Mandate */}
          <div className="card mb-4">
            <div className="card-header">
              <div>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Tier One Mandate</div>
                <div style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>DOC REF: RJ-UDR-2025-09</div>
              </div>
            </div>
            <div className="card-body">
              <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 24, fontWeight: 700, color: 'var(--secondary)', marginBottom: 10 }}>Grand Rajputana Royal Package</h2>
              <p style={{ fontSize: 14, color: 'var(--on-surface-variant)', lineHeight: 1.6 }}>
                Multi-Estate Celebrations across Jagmandir Island Palace, The Oberoi Udaivilas, and Zenana Mahal Courtyard (Udaipur, Rajasthan).
              </p>
            </div>
          </div>

          {/* Retainer & Milestones */}
          <div className="card mb-4">
            <div className="card-header">
              <span className="card-title">I. Retainer &amp; Financial Disbursements</span>
              <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Currency: INR (₹)</span>
            </div>
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Milestone / Deliverable</th>
                    <th>Scheduled Date</th>
                    <th>Status</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {MILESTONES.map((m, i) => (
                    <tr key={i}>
                      <td>
                        <div style={{ fontWeight: 700, fontSize: 14 }}>{m.label}</div>
                        <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginTop: 3 }}>{m.desc}</div>
                      </td>
                      <td style={{ fontSize: 13, fontWeight: 500, whiteSpace: 'nowrap' }}>{m.date}</td>
                      <td>
                        <span className={`badge badge-${m.type}`}>
                          {m.type === 'success' && '✓ '}
                          {m.status}
                        </span>
                      </td>
                      <td style={{ fontWeight: 700, fontSize: 15, fontFamily: "'Playfair Display', serif" }}>{m.amount}</td>
                    </tr>
                  ))}
                  <tr style={{ background: 'var(--surface-container-low)' }}>
                    <td colSpan={2}>
                      <span style={{ fontWeight: 700, fontSize: 15 }}>Total Agency Fee (Inclusive of GST &amp; Luxury Heritage Surcharge)</span>
                    </td>
                    <td />
                    <td>
                      <span style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: 'var(--primary-container)' }}>₹18,50,000</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div style={{ padding: '10px 16px', borderTop: '1px solid var(--beige-border)', fontSize: 12, color: 'var(--on-surface-variant)', fontStyle: 'italic' }}>
              INR Eighteen Lakh Fifty Thousand Only. Excludes actual palace venue rental disbursements paid directly to heritage trusts.
            </div>
          </div>

          {/* Venue image */}
          <div className="card" style={{ overflow: 'hidden' }}>
            <div style={{ position: 'relative', height: 160 }}>
              <img src="https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=800&h=200&fit=crop" alt="Jagmandir Island Palace" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.75), transparent)', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: 16 }}>
                <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--secondary-fixed-dim)', marginBottom: 4 }}>Host Venue</div>
                <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700, color: 'white' }}>Jagmandir Island Palace</div>
                <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.8)' }}>Lake Pichola, Udaipur • Main Wedding Muhurat</div>
              </div>
            </div>
            <div className="card-body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--gold)' }}>star</span>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>5-Star Heritage Protocol</div>
                  <div style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Full venue security &amp; private dock lockdown</div>
                </div>
              </div>
              <button className="btn-secondary" id="view-map-btn" style={{ fontSize: 12 }}>
                View Map <span className="material-symbols-outlined" style={{ fontSize: 14 }}>north_east</span>
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar: digital signature */}
        <div style={{ width: 300, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card">
            <div className="card-header">
              <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--secondary)' }}>Affirmation Desk</span>
              <button className="btn-ghost" style={{ padding: 4 }} id="edit-sig-btn"><span className="material-symbols-outlined" style={{ fontSize: 16 }}>edit</span></button>
            </div>
            <div className="card-body">
              <h3 style={{ fontFamily: "'Playfair Display', serif", fontSize: 20, fontWeight: 700, marginBottom: 14 }}>Digital Signature</h3>
              {[
                { label: 'Primary Signatory:', val: 'Aarav Singhania' },
                { label: 'Signer Role:', val: 'Client & Groom\'s Guardian' },
                { label: 'Heritage Agency Escort:', val: 'Pooja Rathore (Founder)' },
                { label: 'Execution Timestamp:', val: '12 November 2025 • 17:42 IST' },
              ].map(r => (
                <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13 }}>
                  <span style={{ color: 'var(--on-surface-variant)', flexShrink: 0 }}>{r.label}</span>
                  <span style={{ fontWeight: 600, textAlign: 'right' }}>{r.val}</span>
                </div>
              ))}

              {/* Signature canvas */}
              <div style={{ marginTop: 14, marginBottom: 14 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 12 }}>
                  <span style={{ color: 'var(--on-surface-variant)', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 14 }}>edit</span>
                    Client Signature Stroke
                  </span>
                  <button className="btn-ghost" style={{ fontSize: 11, padding: '2px 8px' }} id="clear-canvas-btn">↺ Clear Canvas</button>
                </div>
                <div style={{ background: 'var(--surface-container-low)', border: '1px solid var(--beige-border)', borderRadius: 8, height: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                  <svg viewBox="0 0 250 80" style={{ width: '100%', height: '100%', padding: 16 }}>
                    <path d="M20 60 C40 20, 60 70, 80 40 C100 10, 120 60, 140 45 C160 30, 180 55, 200 35 C210 25, 220 45, 230 40" stroke="var(--primary-container)" strokeWidth="2" fill="none" strokeLinecap="round" />
                  </svg>
                  <div style={{ position: 'absolute', bottom: 6, right: 8, fontSize: 10, color: 'var(--success)', fontWeight: 600 }}>VERIFIED E-SEAL</div>
                </div>
                <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 6, textAlign: 'center' }}>Draw or stylus approved • High sensitivity</div>
              </div>

              {/* Consent checkbox */}
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 14, padding: '10px 12px', background: 'var(--surface-container-low)', borderRadius: 8 }}>
                <div
                  onClick={() => setChecked(c => !c)}
                  style={{ width: 16, height: 16, borderRadius: 3, background: checked ? 'var(--primary-container)' : 'white', border: checked ? 'none' : '1.5px solid var(--outline)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', flexShrink: 0, marginTop: 1 }}
                >
                  {checked && <span className="material-symbols-outlined" style={{ fontSize: 12, color: 'white' }}>check</span>}
                </div>
                <div style={{ fontSize: 12, color: 'var(--on-surface)', lineHeight: 1.5 }}>
                  I have verified the terms, payment milestones (Total ₹18,50,000), cancellation limits, and agree to Rajasthani Heritage Ceremonial event protocols.
                </div>
              </div>

              {/* Execute button */}
              <button
                className="btn-primary"
                style={{ width: '100%', marginBottom: 8 }}
                id="execute-signature-btn"
                onClick={() => setSigned(true)}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{signed ? 'verified' : 'draw'}</span>
                {signed ? '✓ Signature Executed' : 'Execute Binding Signature'} →
              </button>
              <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', textAlign: 'center', marginBottom: 14 }}>Timestamp &amp; IP address recorded upon submission.</div>

              {/* Cert details */}
              <div style={{ background: 'var(--surface-container-low)', border: '1px solid var(--beige-border)', borderRadius: 8, padding: 12, fontSize: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--success)' }}>verified</span>
                    Signature Certified &amp; Stamped
                  </span>
                  <span className="badge badge-success" style={{ fontSize: 10 }}>Valid E-Contract</span>
                </div>
                {[
                  { k: 'Cert Serial:', v: 'MH-RAJ-2025-0987-AX' },
                  { k: 'Signature Hash:', v: 'SHA256: 8f9b7c...3c12' },
                  { k: 'Rajasthan Node:', v: 'Udaipur City Center (Zone 2)' },
                ].map(r => (
                  <div key={r.k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ color: 'var(--on-surface-variant)' }}>{r.k}</span>
                    <span style={{ fontWeight: 600, fontSize: 11 }}>{r.v}</span>
                  </div>
                ))}
                <div style={{ marginTop: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 13, color: 'var(--secondary)' }}>lock</span>
                  <span style={{ color: 'var(--on-surface-variant)', fontSize: 11 }}>Immutable Tamper-Evident Record</span>
                  <button className="btn-ghost" style={{ fontSize: 11, padding: '2px 6px' }} id="view-audit-trail-btn">View Audit Trail</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
