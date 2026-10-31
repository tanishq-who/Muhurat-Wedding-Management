import { useState } from 'react'

const VENDORS = [
  { name: 'Rajwada Caterers', cat: 'Culinary & Banquets', agreed: '₹11,80,000', actual: '₹12,52,000', advance: '₹9,00,000', remaining: '₹3,52,000', variance: '+₹72,000', varNote: '+60 extra plates requested midnight', status: 'Disburse', disbAmt: '₹3.52L', varType: 'warning' },
  { name: 'Rathore Heritage Florals', cat: 'Mandap Architecture & Stage Decor', agreed: '₹32,00,000', actual: '₹34,20,000', advance: '₹25,00,000', remaining: '₹9,20,000', variance: '+₹2,20,000', varNote: '+Additional Rajnigandha & cold pyros', status: 'Disputed', disbAmt: '', varType: 'danger', note: 'Audit Pending on delivery slips' },
  { name: 'Udaipur Royal Boat Ferries', cat: 'Lake Pichola Flotilla & VIP Shikaras', agreed: '₹8,50,000', actual: '₹8,50,000', advance: '₹8,50,000', remaining: '₹0', variance: '✓ Exact to contract', varNote: '', status: 'Paid & Closed', disbAmt: '', varType: 'success' },
  { name: 'SkyMagic Drone Pyrotechnics', cat: 'Aerial Synchronized Light Show (600 Drones)', agreed: '₹14,00,000', actual: '₹14,00,000', advance: '₹10,50,000', remaining: '₹3,50,000', variance: 'Retainer clearance', varNote: '', status: 'Disburse', disbAmt: '₹3.50L', varType: 'neutral' },
  { name: 'Sound & Acoustic Pro', cat: 'Jodhpur Line Array Rigging & Tech Crew', agreed: '₹6,50,000', actual: '₹7,10,000', advance: '₹5,00,000', remaining: '₹2,10,000', variance: '+₹60,000', varNote: '+Extended DJ curfew 2.5 hrs', status: 'Disburse', disbAmt: '₹2.10L', varType: 'warning' },
  { name: 'Manganiyar Folk Troupe & Shehnai Ensemble', cat: 'Ceremonial Sangeet & Welcome Procession', agreed: '₹3,80,000', actual: '₹3,80,000', advance: '₹3,80,000', remaining: '₹0', variance: 'Completed full roster', varNote: '', status: 'Paid & Closed', disbAmt: '', varType: 'success' },
  { name: 'House of Sabyasachi & Bridal Draping Valet', cat: 'Couture Pressing, Steam Vault & Trousseau', agreed: '₹5,20,000', actual: '₹5,20,000', advance: '₹5,20,000', remaining: '₹0', variance: 'Nil discrepancies', varNote: '', status: 'Paid & Closed', disbAmt: '', varType: 'success' },
]

const INCIDENTALS = [
  { icon: '🍛', color: '#fef8e7', label: '60 Extra Banquet Dinner Covers @ ₹1,200', by: 'Rajwada Caterers • Billable to Client • Approved by Host', amount: '₹72,000' },
  { icon: '🎵', color: '#fdecee', label: 'DJ Curfew Extension (2.5 hrs post 10 PM sound compliance)', by: 'Sound & Acoustic Pro • District Admin Liaison Fee • Approved', amount: '₹60,000' },
]

export default function Settlement() {
  const [disbursed, setDisbursed] = useState({})

  return (
    <div className="page-canvas animate-fade-in">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span className="material-symbols-outlined">receipt_long</span>
        Post-Event Audit &amp; Reconciliation
        <span style={{ color: 'var(--on-surface-variant)', textTransform: 'none', letterSpacing: 0, fontWeight: 400 }}>• Folio #RK-UD-2027-041</span>
      </div>

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Post-Event Settlement &amp;<br />Vendor Reconciliation</h1>
          <div style={{ fontSize: 14, color: 'var(--on-surface)', fontWeight: 600, marginTop: 6 }}>Aarav Singhania &amp; Meera Kapoor</div>
          <div style={{ display: 'flex', gap: 12, marginTop: 4, flexWrap: 'wrap', fontSize: 13, color: 'var(--on-surface-variant)' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="material-symbols-outlined" style={{ fontSize: 13 }}>calendar_month</span> 14 Feb 2027</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><span className="material-symbols-outlined" style={{ fontSize: 13 }}>location_on</span> Udaipur Jagmandir Island &amp; Udaivilas</span>
          </div>
          <span className="badge badge-success" style={{ marginTop: 8 }}>● Completed (19 Feb 2027)</span>
        </div>
        <div className="page-actions">
          <button className="btn-ghost" id="export-audit-btn"><span className="material-symbols-outlined">table_chart</span> Export Audit Ledger (XLSX)</button>
          <button className="btn-secondary" id="download-settlement-btn"><span className="material-symbols-outlined">picture_as_pdf</span> Download Settlement Dossier (PDF)</button>
          <button className="btn-primary" id="record-payment-btn"><span className="material-symbols-outlined">add</span> + Record Payment</button>
        </div>
      </div>

      {/* Top KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 16, marginBottom: 20 }}>
        <div className="kpi-card">
          <div className="kpi-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 13 }}>account_balance</span>
            Client Total Receivable
          </div>
          <div className="kpi-value" style={{ fontSize: 36 }}>₹3,42,80,000</div>
          <div className="kpi-sub">Base: ₹3.20 Cr &nbsp;+&nbsp; Extras: ₹22.80 L</div>
          <div className="kpi-sub" style={{ marginTop: 4 }}>Billed to Singhania Estate • ₹2.95 Cr Collected (86%)</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 13 }}>groups</span>
            Vendor Total Payable
          </div>
          <div className="kpi-value" style={{ fontSize: 36 }}>₹2,18,45,000</div>
          <div className="kpi-sub">Contracted: 9 Vendors &nbsp;•&nbsp; Variance: +₹11,25,000</div>
          <div className="kpi-sub" style={{ marginTop: 4 }}>₹1,72,50,000 Advance Disbursed • Base: ₹2,07,20,000</div>
        </div>
        <div style={{ background: 'var(--primary-container)', borderRadius: 10, padding: 16, minWidth: 200 }}>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'rgba(255,255,255,0.7)', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 13 }}>account_balance_wallet</span>
            Balance to Collect from Client
          </div>
          <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 32, fontWeight: 700, color: 'white', lineHeight: 1 }}>₹47,80,000</div>
          <div style={{ marginTop: 8, borderTop: '1px solid rgba(255,255,255,0.15)', paddingTop: 8 }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.75)' }}>Due: 22 Feb 2027 &nbsp; Agency Margin: 36.2%</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.6)', marginTop: 2 }}>Net Agency Retainer Margin: ₹1,24,35,000</div>
          </div>
        </div>
      </div>

      {/* Vendor reconciliation table */}
      <div className="card mb-4">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>receipt_long</span>
            <span className="card-title">Vendor Bills &amp; Cost Variance Audit</span>
          </div>
          <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="badge badge-warning"><span className="material-symbols-outlined" style={{ fontSize: 12 }}>warning</span> 3 Overruns Identified</span>
          </span>
        </div>
        <p style={{ padding: '8px 16px', fontSize: 12, color: 'var(--on-surface-variant)', borderBottom: '1px solid var(--beige-border)' }}>Granular reconciliation across contracted suppliers, variance authorizations, and escrow releases.</p>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Vendor &amp; Service Category</th>
                <th>Agreed Contract</th>
                <th>Actual Incurred</th>
                <th>Advance Paid</th>
                <th>Remaining Balance</th>
                <th>Variance &amp; Notes</th>
                <th>Settlement Status</th>
              </tr>
            </thead>
            <tbody>
              {VENDORS.map((v, i) => (
                <tr key={i}>
                  <td>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{v.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>{v.cat}</div>
                  </td>
                  <td style={{ fontWeight: 600 }}>{v.agreed}</td>
                  <td style={{ fontWeight: 600 }}>{v.actual}</td>
                  <td style={{ fontWeight: 600 }}>{v.advance}</td>
                  <td style={{ fontWeight: 700 }}>{v.remaining}</td>
                  <td>
                    {v.variance && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        {v.varType !== 'success' && v.varType !== 'neutral' && (
                          <span className={`badge badge-${v.varType}`} style={{ fontSize: 10 }}>{v.variance}</span>
                        )}
                        {(v.varType === 'success' || v.varType === 'neutral') && (
                          <span style={{ fontSize: 12, color: 'var(--success)', fontWeight: 500 }}>{v.variance}</span>
                        )}
                      </div>
                    )}
                    {v.varNote && <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 3 }}>{v.varNote}</div>}
                  </td>
                  <td>
                    {v.status === 'Paid & Closed' && (
                      <span className="badge badge-neutral" style={{ fontSize: 11 }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 12 }}>check_circle</span>
                        Paid & Closed
                      </span>
                    )}
                    {v.status === 'Disputed' && (
                      <div>
                        <span className="badge badge-danger" style={{ fontSize: 11, marginBottom: 4 }}>Disputed</span>
                        <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>{v.note}</div>
                      </div>
                    )}
                    {v.status === 'Disburse' && !disbursed[i] && (
                      <button
                        className="btn-primary"
                        style={{ fontSize: 11, padding: '5px 10px' }}
                        id={`disburse-${i}-btn`}
                        onClick={() => setDisbursed(d => ({ ...d, [i]: true }))}
                      >
                        Disburse {v.disbAmt}
                      </button>
                    )}
                    {v.status === 'Disburse' && disbursed[i] && (
                      <span className="badge badge-success" style={{ fontSize: 11 }}>✓ Disbursed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Pending disbursals footer */}
        <div style={{ padding: '12px 16px', borderTop: '1px solid var(--beige-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--secondary)', display: 'inline-block' }} />
            Pending Disbursals Queue: ₹18,32,000 across 3 vendors (Excludes ₹9.20L disputed).
          </div>
          <button className="btn-primary" id="approve-batch-btn" style={{ fontSize: 12 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>verified</span>
            Approve Batch Payout (₹9,12,000)
          </button>
        </div>
      </div>

      {/* Bottom panels */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 20 }}>
        {/* Incidentals panel */}
        <div className="card">
          <div className="card-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>add_shopping_cart</span>
              <span className="card-title">Incidentals &amp; Extras Management</span>
            </div>
            <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Audit Entry</span>
          </div>
          <div className="card-body">
            <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginBottom: 14 }}>Record on-site client authorizations, midnight hospitality additions, and city compliance extensions to bill to the Singhania Folio.</p>
            {/* Quick-entry form */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
              <div className="form-group">
                <label className="form-label">Service Category</label>
                <select className="form-input" id="incidental-category-select">
                  <option>Culinary &amp; Banquets</option>
                  <option>Logistics</option>
                  <option>Entertainment</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Vendor Attribution</label>
                <select className="form-input" id="incidental-vendor-select">
                  <option>Rajwada Caterers</option>
                  <option>Sound &amp; Acoustic Pro</option>
                </select>
              </div>
            </div>
            <div className="form-group" style={{ marginBottom: 12 }}>
              <label className="form-label">Incident Description &amp; Authorization Tag</label>
              <input className="form-input" id="incidental-desc" placeholder="60 extra plates @ ₹1,200 (Late Night Biryani Counters)" />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12, marginBottom: 14 }}>
              <div className="form-group">
                <label className="form-label">Quantity</label>
                <input className="form-input" id="incidental-qty" type="number" defaultValue="60" />
              </div>
              <div className="form-group">
                <label className="form-label">Rate (₹)</label>
                <input className="form-input" id="incidental-rate" type="number" defaultValue="1200" />
              </div>
              <div className="form-group">
                <label className="form-label">Auto Subtotal</label>
                <div className="form-input" style={{ background: 'var(--warning-bg)', fontWeight: 700, color: 'var(--secondary)' }}>₹72,000</div>
              </div>
            </div>
            <button className="btn-primary" style={{ width: '100%' }} id="add-incidental-btn">
              <span className="material-symbols-outlined">add_circle</span>
              + Add to Client Invoice
            </button>

            <div className="divider" />
            <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginBottom: 10, display: 'flex', justifyContent: 'space-between' }}>
              <span>Logged Incidentals on Folio (4 items)</span>
              <span>Subtotal: ₹2,72,000</span>
            </div>
            {INCIDENTALS.map((inc, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 10, padding: '10px 12px', background: inc.color, borderRadius: 8 }}>
                <div style={{ width: 28, height: 28, borderRadius: 6, background: 'rgba(0,0,0,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0 }}>{inc.icon}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 12, color: 'var(--on-surface)' }}>{inc.label}</div>
                  <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 1 }}>{inc.by}</div>
                </div>
                <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--on-surface)', flexShrink: 0 }}>{inc.amount}</div>
                <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--on-surface-variant)', padding: 0 }} id={`remove-incidental-${i}-btn`}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>delete</span>
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Invoice panel */}
        <div className="card" style={{ minWidth: 280, maxWidth: 320 }}>
          <div className="card-header" style={{ background: 'var(--surface-container-low)' }}>
            <div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 16, fontWeight: 700 }}>The Royal Knot</div>
              <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>Settlement Dossier</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 10, fontWeight: 600, color: 'var(--on-surface-variant)' }}>Invoice Number</div>
              <div style={{ fontSize: 11, fontWeight: 700 }}>INV-SINGH-2027-POST</div>
            </div>
          </div>
          <div className="card-body">
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--on-surface-variant)', marginBottom: 8 }}>Client Folio &amp; Principal Billing</div>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>Mr. Aarav Singhania &amp; Dr. Meera Kapoor</div>
            <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginBottom: 14 }}>Singhania Industrial House • C/o The Udaivilas &amp; Jagmandir Island</div>

            {[
              { label: 'Master Heritage Wedding Package (Contracted)', amount: '₹3,20,00,000', align: 'right' },
              { label: 'Post-Event Extras & Incidentals (4 items)', amount: '+₹2,72,000', align: 'right' },
            ].map(r => (
              <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 8 }}>
                <span style={{ color: 'var(--on-surface-variant)' }}>{r.label}</span>
                <span style={{ fontWeight: 600 }}>{r.amount}</span>
              </div>
            ))}
            <div style={{ borderTop: '1px solid var(--beige-border)', paddingTop: 8, marginBottom: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, fontSize: 14 }}>
                <span>Gross Folio Total</span>
                <span>₹3,22,72,000</span>
              </div>
            </div>
            {[
              { label: 'Less: Advance Tranche 01 (Token Reservation)', amount: '-₹35,00,000' },
              { label: 'Less: Advance Tranche 02 (50% Mobilization)', amount: '-₹1,25,00,000' },
              { label: 'Less: Mid-Event Escrow Deposit (Pre-Sangeet)', amount: '-₹14,92,000' },
            ].map(r => (
              <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, color: 'var(--on-surface-variant)', marginBottom: 6 }}>
                <span>{r.label}</span>
                <span>{r.amount}</span>
              </div>
            ))}

            <div style={{ background: 'var(--primary-container)', borderRadius: 8, padding: '14px', marginTop: 14, marginBottom: 14 }}>
              <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'rgba(255,255,255,0.7)' }}>Outstanding Final Balance Due</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 28, fontWeight: 700, color: 'white', lineHeight: 1.1, marginTop: 4 }}>₹47,80,000</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.7)', marginTop: 4 }}>Net reconciliation after all approved deductions</div>
            </div>

            <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginBottom: 14, display: 'flex', alignItems: 'flex-start', gap: 6 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 13, marginTop: 1 }}>info</span>
              Payment Terms & Settlement Date: Due within 7 business days by 23 Feb 2027 via HDFC Escrow Vault or RTGS transfer directly to The Royal Knot Client Trust Account.
            </div>

            <button className="btn-primary" style={{ width: '100%', marginBottom: 8 }} id="generate-invoice-btn">
              Generate Final Invoice &amp; Dispatch to Client <span className="material-symbols-outlined" style={{ fontSize: 14 }}>arrow_forward</span>
            </button>
            <button className="btn-ghost" style={{ width: '100%', fontSize: 12 }} id="preview-pdf-btn">
              <span className="material-symbols-outlined" style={{ fontSize: 14 }}>preview</span>
              Preview Formal PDF Dossier
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
