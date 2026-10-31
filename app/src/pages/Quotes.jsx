import { useState } from 'react'

const CATERERS = [
  {
    name: 'Rajwada Caterers',
    sub: 'Heritage Rajasthani & Continental • Udaipur',
    rating: '4.9', reviews: 120, cert: 'FSSAI Top Tier',
    items: ['₹2,60,000', '₹4,80,000', '₹1,80,000', '₹1,10,000', '₹90,000', '₹60,000'],
    subtotal: '₹11,80,000', gst: '₹11,80,000',
    perPax: '₹2,950', tag: 'Lowest Price / Best Value', tagType: 'success',
    delta: null,
  },
  {
    name: 'Shahi Rasoi',
    sub: 'Royal Mughlai & Modern Fusion • Jaipur',
    rating: '4.8', reviews: 95, cert: 'FSSAI Certified',
    items: ['₹2,90,000', '₹5,10,000', '₹2,10,000', '₹1,30,000', '₹1,05,000', '₹75,000'],
    subtotal: '₹13,20,000', gst: '₹13,20,000',
    perPax: '₹3,300', tag: '+₹350 / plate vs Lowest', tagType: 'neutral',
    delta: '+₹350/plate',
  },
  {
    name: 'Mehfil Foods',
    sub: 'Bespoke Banquets & Molecular • Delhi',
    rating: '4.7', reviews: 80, cert: 'Luxury Accredited',
    items: ['₹3,10,000', '₹5,40,000', '₹2,20,000', '₹1,50,000', '₹1,20,000', '₹80,000'],
    subtotal: '₹14,30,000', gst: '₹14,30,000',
    perPax: '₹3,575', tag: '+₹625 / plate vs Lowest', tagType: 'danger',
    delta: '+₹625/plate',
  },
]

const MODULES = [
  { label: '1. Starters & Canapés', detail: '8 Veg / 4 Live Charcoal Grills', location: 'Pre-function Terrace' },
  { label: '2. Royal Main Course', detail: '14 Entrees, 4 Dal & Biryani, Artisanal Breads', location: 'Mewar Grand Banquet' },
  { label: '3. Thematic Live Stations', detail: '4 Fully Styled Culinary Experience Counters', location: 'Courtyard Jharokha Zone' },
  { label: '4. Desserts & Mithai', detail: '8 Artisanal & Warm Rajasthani Sweets', location: 'Halwai Master Stations' },
  { label: '5. Staffing & Butler Brigade', detail: '45 Trained Stewards, 6 Station Chefs', location: 'Guest Attendant Ratio 1:9' },
  { label: '6. Eco-Logistics & Kitchen Cleanliness', detail: 'HACCP, Solid Waste Audit, Kitchen Clearance', location: 'Palace Green Protocol' },
]

export default function Quotes() {
  const [selected, setSelected] = useState(null)

  return (
    <div className="page-canvas animate-fade-in">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span className="material-symbols-outlined">restaurant</span>
        Banqueting &amp; Culinary RFP Dossier
        <span style={{ color: 'var(--on-surface-variant)', fontWeight: 400, textTransform: 'none', letterSpacing: 0 }}>• Folio: #QUO-2025-412</span>
      </div>

      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Caterer Quote Comparison</h1>
          <p className="page-subtitle" style={{ fontSize: 13 }}>
            <strong>Kabir Joshi &amp; Radhika Merchant</strong> &nbsp;•&nbsp; 400 Guests &nbsp;•&nbsp; Mewar Banquet &amp; Lake Terrace &nbsp;•&nbsp; Rajputana &amp; Global Gastronomy
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 }}>
            <span className="badge badge-neutral"><span className="material-symbols-outlined" style={{ fontSize: 12 }}>group</span> 400 Pax Confirmed</span>
            <span className="badge badge-gold"><span className="material-symbols-outlined" style={{ fontSize: 12 }}>eco</span> Dietary: Royal Pure Veg &amp; Marwari Delicacies</span>
            <span className="badge badge-warning"><span className="material-symbols-outlined" style={{ fontSize: 12 }}>gavel</span> Status: Active Vendor Bidding</span>
            <span className="badge badge-neutral"><span className="material-symbols-outlined" style={{ fontSize: 12 }}>calendar_month</span> Dec 14–16, 2025</span>
          </div>
        </div>
        <div className="page-actions">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, alignItems: 'flex-end' }}>
            <div style={{ display: 'flex', gap: 8 }}>
              <div style={{ padding: '8px 12px', background: 'var(--primary-container)', color: 'white', borderRadius: 8, fontSize: 12, fontWeight: 700, textAlign: 'center' }}>
                Comparing<br /><span style={{ fontSize: 11, fontWeight: 500 }}>(3 Active Quotes)</span>
              </div>
              <div style={{ padding: '8px 12px', background: 'var(--surface-container-high)', color: 'var(--on-surface-variant)', borderRadius: 8, fontSize: 12, fontWeight: 600, textAlign: 'center' }}>
                Decided<br /><span style={{ fontSize: 11, fontWeight: 400 }}>(Winner Selected)</span>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn-secondary" id="export-pdf-btn"><span className="material-symbols-outlined">picture_as_pdf</span> Export PDF</button>
              <button className="btn-primary" id="add-vendor-quote-btn"><span className="material-symbols-outlined">add</span> Add Vendor Quote</button>
            </div>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid-3 mb-4">
        <div className="kpi-card">
          <div className="kpi-label">Allocated Cap</div>
          <div className="kpi-value">₹3,200 <span style={{ fontSize: 14, fontWeight: 500 }}>/pax</span></div>
          <div className="kpi-sub">Total Budget Ceiling — ₹12,80,000</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Average RFP Bid</div>
          <div className="kpi-value">₹3,175 <span style={{ fontSize: 14, fontWeight: 500 }}>/plate</span></div>
          <div className="kpi-sub">Aggregated Average — ₹12,70,000 Total</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-label">Best Value Spread</div>
          <div className="kpi-value">₹90,000 <span style={{ fontSize: 14, fontWeight: 400 }}>Savings Cap</span></div>
          <div className="kpi-sub" style={{ color: 'var(--success)', fontWeight: 600 }}>Rajwada Caterers — 7.03% Under Cap</div>
        </div>
      </div>

      {/* Cuisine feature images */}
      <div className="grid-3 mb-4">
        {[
          { label: 'Heritage Tasting', title: 'Traditional Marwari Thali Feast', img: 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&h=160&fit=crop' },
          { label: 'Live Stations', title: 'Four Thematic Interactive Grills', img: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=160&fit=crop' },
          { label: 'Mithai & Patisserie', title: 'Royal Sweets & Modern Confections', img: 'https://images.unsplash.com/photo-1571506165871-ee72a35bc9d4?w=400&h=160&fit=crop' },
        ].map(({ label, title, img }) => (
          <div key={title} className="img-overlay" style={{ borderRadius: 10, overflow: 'hidden', height: 130 }}>
            <img src={img} alt={title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.7), transparent)', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: 12 }}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--secondary-fixed-dim)', marginBottom: 2 }}>{label}</div>
              <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 15, fontWeight: 700, color: 'white', lineHeight: 1.25 }}>{title}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Table */}
      <div className="card mb-4">
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>table_chart</span>
            <span className="card-title">Detailed Quotation Breakdown</span>
            <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>(400 Guests Standardized Base)</span>
          </div>
          <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>verified</span> All taxes &amp; logistics inclusive
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 200 }}>Evaluation Criteria — Culinary Modules</th>
                {CATERERS.map(c => (
                  <th key={c.name}>
                    <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 14, fontWeight: 700, textTransform: 'none', letterSpacing: 0, color: 'var(--on-surface)' }}>{c.name}</div>
                    <div style={{ fontWeight: 400, fontSize: 11, textTransform: 'none', letterSpacing: 0 }}>{c.sub}</div>
                    <div style={{ display: 'flex', gap: 4, marginTop: 4 }}>
                      <span className="badge badge-gold" style={{ fontSize: 10 }}>⭐ {c.rating} ({c.reviews} weddings)</span>
                      <span className="badge badge-success" style={{ fontSize: 10 }}>{c.cert}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MODULES.map((mod, i) => (
                <tr key={mod.label}>
                  <td>
                    <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--on-surface)' }}>{mod.label}</div>
                    <div style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>{mod.detail}</div>
                    <div style={{ fontSize: 11, color: 'var(--secondary)', fontWeight: 600, marginTop: 2 }}>{mod.location}</div>
                  </td>
                  {CATERERS.map(c => (
                    <td key={c.name} style={{ fontWeight: 600, fontSize: 14 }}>{c.items[i]}</td>
                  ))}
                </tr>
              ))}
              {/* Financial summary row */}
              <tr style={{ background: 'var(--surface-container-low)' }}>
                <td>
                  <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: 'var(--on-surface-variant)', marginBottom: 4 }}>Financial Summary</div>
                  <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 16, fontWeight: 700 }}>Net Cost / Pax</div>
                  <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>Inclusive of 18% Banqueting GST</div>
                </td>
                {CATERERS.map((c, i) => (
                  <td key={c.name}>
                    <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginBottom: 4 }}>Subtotal + GST: {c.subtotal}</div>
                    <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: i === 0 ? 'var(--success)' : 'var(--on-surface)' }}>{c.perPax} <span style={{ fontSize: 12, fontWeight: 400 }}>/pax</span></div>
                    {c.tagType === 'success'
                      ? <span className="badge badge-success" style={{ marginTop: 4 }}>{c.tag}</span>
                      : <span style={{ fontSize: 11, color: 'var(--on-surface-variant)', marginTop: 4, display: 'block' }}>{c.tag}</span>
                    }
                  </td>
                ))}
              </tr>
              {/* Select winner row */}
              <tr>
                <td><span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Operational Decision</span></td>
                {CATERERS.map((c, i) => (
                  <td key={c.name}>
                    <button
                      className={selected === i ? 'btn-primary' : 'btn-secondary'}
                      style={{ width: '100%' }}
                      id={`select-winner-${i}-btn`}
                      onClick={() => setSelected(i)}
                    >
                      {selected === i ? '✓ Selected Winner' : 'Select Winner'} <span className="material-symbols-outlined" style={{ fontSize: 14 }}>arrow_forward</span>
                    </button>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom panels */}
      <div className="grid-3">
        {/* Tasting notes */}
        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: 15 }}>Tasting Committee Notes</span>
            <span className="badge badge-success">Session Complete</span>
          </div>
          <div className="card-body" style={{ fontSize: 13 }}>
            {[
              { name: 'Rajwada Caterers (Nov 2)', score: '9.6 / 10', note: '"Dal Baati and Gatta Curry received unanimous acclaim from Joshi elders. Ker Sangri flavor balanced exceptionally well."' },
              { name: 'Shahi Rasoi (Nov 4)', score: '8.9 / 10', note: '"Biryani and Chaat bar were excellent. Paneer gravy deemed slightly richer than requested for late-night reception dining."' },
            ].map(t => (
              <div key={t.name} style={{ marginBottom: 14 }}>
                <div style={{ fontWeight: 700, color: 'var(--on-surface)', marginBottom: 3 }}>{t.name} <span style={{ color: 'var(--secondary)', fontWeight: 600 }}>{t.score}</span></div>
                <div style={{ color: 'var(--on-surface-variant)', fontStyle: 'italic', lineHeight: 1.5 }}>{t.note}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Payment tranches */}
        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: 15 }}>Payment Tranches</span>
            <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Standard Folio Policy</span>
          </div>
          <div className="card-body">
            {[
              { num: 1, label: '25% Token Advance', when: 'At Agreement Signing' },
              { num: 2, label: '50% Kitchen Mobilization', when: 'T-14 Days Pre-Event' },
              { num: 3, label: '25% Final Settlement', when: 'Post-Reception Audit' },
            ].map(t => (
              <div key={t.num} style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 14 }}>
                <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--primary-container)', color: 'white', fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{t.num}</div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{t.label}</div>
                  <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>{t.when}</div>
                </div>
              </div>
            ))}
            <div style={{ fontSize: 11, color: 'var(--on-surface-variant)', borderTop: '1px solid var(--beige-border)', paddingTop: 10 }}>
              Escrow held via The Royal Knot Client Trust Ledger.
            </div>
          </div>
        </div>

        {/* Palace compliance */}
        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: 15 }}>Palace Venue Compliance</span>
            <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Mewar Rules</span>
          </div>
          <div className="card-body">
            {[
              { icon: 'check_circle', text: 'Pure Vegetarian Requirement: Venue strictly prohibits non-vegetarian ingredients on Mewar Banquet premises.' },
              { icon: 'local_fire_department', text: 'Heritage Flame Policy: Open wood-fire grilling confined exclusively to designated North Courtyard Jharokha zone.' },
              { icon: 'badge', text: 'Staff Background Check: All 45 service personnel must wear registered photo identity passes issued by Palace Security.' },
            ].map((c, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 12, fontSize: 12, color: 'var(--on-surface-variant)', lineHeight: 1.5 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 15, color: 'var(--success)', flexShrink: 0, marginTop: 1 }}>{c.icon}</span>
                {c.text}
              </div>
            ))}
            <div style={{ marginTop: 8, fontSize: 12, color: 'var(--on-surface-variant)', display: 'flex', justifyContent: 'space-between' }}>
              <span>Lead Coordinator: <strong>Pooja Rathore</strong></span>
              <span className="badge badge-primary">Heritage Ops HQ</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
