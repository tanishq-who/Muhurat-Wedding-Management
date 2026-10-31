const TIMELINE_EVENTS = [
  { time: '06:00\nAM IST', status: 'done', location: 'Jagmandir Courtyard', title: 'Mandap Structural Inspection & Holy Water Sanctification', desc: 'Sanctification completed at sunrise with Gangajal & Narmada waters. Structural engineer and chief priest sign-off completed.', planner: 'Devika Rao', vendor: 'Vedic Priests of Mewar & Royal Structurals', logged: 'Logged 06:32 AM' },
  { time: '07:00\nAM IST', status: 'in-progress', location: 'Taj Lake Palace • Suite 102', title: 'Bridal Suite & Hair-Makeup Commencement', desc: 'Bridal party styling in Lake Palace Suite 102. Custom gold zardozi lehenga unpacked & steamed under white-glove supervision.', planner: 'Priya Sharma', vendor: 'House of Sabyasachi & Ojas Rajani Glam Team', logged: 'In Progress' },
  { time: '07:30\nAM IST', status: 'late', location: 'Mandap Pavilion East', title: 'Floral Decorators & Mandap Marigold-Jasmine Canopy Setup', desc: '45 min delayed at Udaipur Lake Jetty checkpoint. Fragile Dutch roses and rajnigandha strings pending installation on central mandap arch.', planner: 'Priya Sharma', vendor: 'Rathore Heritage Florals (Jaipur)', alert: 'Late (45 min overdue)', actions: ['Mark Arrived', 'Track GPS Float'] },
  { time: '09:30\nAM IST', status: 'pending', location: 'Zenana Mahal Courtyard', title: 'Auspicious Ganesh Puja & Haldi Touch-Up', desc: 'Scheduled for Zenana Mahal Courtyard. 108 Brass diyas ready; turmeric pastes blended with saffron and Chandan from Nathdwara.', planner: 'Devika Rao', vendor: 'Pandit Shastri Ji & Manganiyar Folk Troupe' },
  { time: '11:30\nAM IST', status: 'pending', location: 'The Promenade Terrace', title: 'Royal High Tea & Flute Symphony for Early Arrivals', desc: 'Signature silver samovars, Kashmiri kahwa, and artisanal Rajasthani snacks. Raga Bhairav sitarists seated on floating stage.', planner: 'Rohan Mehta', vendor: 'Rajwada Caterers & Royal Mewar Sitarists' },
  { time: '02:00\nPM IST', status: 'pending', location: 'Lake Pichola Main Pier', title: 'Lake Pichola Flotilla & Royal Baraat Assembly', desc: 'Fleet of 14 velvet-canopied wooden boats marshalling at Udaivilas ghats. Groom\'s royal Marwari stud horse arrives via mainland jetty.', planner: 'Aryan Sharma', vendor: 'Udaipur Royal Boat Ferries & Marwari Stud Horses' },
  { time: '04:30\nPM IST', status: 'pending', location: 'Jagmandir Island Jetty', title: 'Baraat Arrival & Royal Dholak Welcome at Jagmandir Jetty', desc: 'Aerial drone rose petal shower synchronized with 21-cannon flower salute. Bride\'s family tilak ceremony at the marble elephant portal.', planner: 'Aryan Sharma', vendor: 'Nagada Ensemble & Rose Petal Shower Aerial Drones' },
  { time: '05:45\nPM IST', status: 'gold', location: 'Godhuli Muhurat', title: 'Sacred Sunset Pheras & Auspicious Muhurat Vows', desc: 'Sacred 7 Vows around holy Agni kund as the sunset strikes Lake Pichola water line. Gatbandhan ceremony led by Raj Pandit.', planner: 'Devika Rao & Pooja Rathore', vendor: 'Mewar Royal Vedic Council', isGolden: true },
  { time: '08:00\nPM IST', status: 'pending', location: 'The Royal Pavilions', title: 'Grand Royal Feast & Dinner Service Commences', desc: '460 Pax Silver-service banquet featuring royal Mewari recipes, Dal Baati Churma cooked in pure desi ghee, and French pastry installations.', planner: 'Rohan Mehta', vendor: 'Rajwada Caterers (400 Pax Banquet Protocol)' },
  { time: '10:00\nPM IST', status: 'pending', location: 'Lake Pichola Aerial Space', title: 'Lake Pichola Drone Light Show & Fireworks Symphony', desc: '500 Synchronized luminous drones depicting the couple\'s monogram over Lake Pichola followed by low-smoke Italian fireworks.', planner: 'Aryan Sharma', vendor: 'SkyMagic Drone Pyrotechnics' },
]

const STATUS_MAP = {
  done: { dot: 'done', icon: 'check_circle', color: 'var(--success)', label: 'Arrived' },
  'in-progress': { dot: 'active', icon: 'radio_button_checked', color: 'var(--secondary)', label: 'In Progress' },
  late: { dot: 'late', icon: 'warning', color: 'var(--danger)', label: 'Late' },
  pending: { dot: '', icon: 'radio_button_unchecked', color: 'var(--outline)', label: 'Pending' },
  gold: { dot: 'gold', icon: 'brightness_5', color: 'var(--gold)', label: 'Muhurat' },
}

export default function MuhuratTimeline() {
  return (
    <div className="page-canvas animate-fade-in">
      {/* Breadcrumb */}
      <div className="breadcrumb">
        <span className="material-symbols-outlined">satellite_alt</span>
        Critical Operations Console • Udaipur Sector Alfa
      </div>

      {/* Page header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Muhurat Timeline — Wedding Day Execution</h1>
          <p style={{ fontSize: 13, color: 'var(--on-surface-variant)', marginTop: 4 }}>
            Folio #RK-UD-2027-041 • Aarav Singhania &amp; Meera Kapoor ▾<br />
            📅 14 Feb 2027 &nbsp; 🏛 Jagmandir Island &amp; The Oberoi Udaivilas
          </p>
        </div>
        <div className="page-actions">
          <button className="btn-secondary" id="broadcast-alert-btn">
            <span className="material-symbols-outlined">campaign</span>
            Broadcast Alert to Radios
          </button>
          <button className="btn-primary" id="export-runofday-btn">
            <span className="material-symbols-outlined">picture_as_pdf</span>
            Export Run-of-Day PDF
          </button>
        </div>
      </div>

      {/* Chrono status bar */}
      <div className="card mb-4">
        <div className="card-body" style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--on-surface-variant)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span className="material-symbols-outlined" style={{ fontSize: 12 }}>timer</span> Chronometer
              <span className="badge badge-success" style={{ fontSize: 10 }}>Synced Satellite GPS</span>
            </div>
            <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 36, fontWeight: 700, color: 'var(--on-surface)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>08:15:49</div>
            <div style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>AM IST</div>
            <div style={{ marginTop: 8, background: 'var(--warning-bg)', border: '1px solid rgba(224,161,0,0.2)', borderRadius: 6, padding: '6px 10px', fontSize: 12 }}>
              <div style={{ fontWeight: 700, color: 'var(--secondary)' }}>Sunset Phera Muhurat</div>
              <div style={{ color: 'var(--on-surface)' }}>05:45 PM (Godhuli Lagna)</div>
              <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>TARGET WINDOW: 09h 29m rem.</div>
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, auto)', gap: '0 24px', alignSelf: 'flex-start' }}>
            {[
              { label: 'Total Run', value: '16', sub: 'Milestone protocols', icon: 'checklist', color: 'var(--on-surface)' },
              { label: 'On Schedule', value: '11', sub: 'Clear & Staged', icon: 'check_circle', color: 'var(--success)' },
              { label: 'Pending Staging', value: '3', sub: 'Upcoming transitions', icon: 'schedule', color: 'var(--warning)' },
              { label: 'Late / At Risk', value: '1', sub: 'Critical mandap floral', icon: 'warning', color: 'var(--danger)' },
            ].map(s => (
              <div key={s.label} style={{ textAlign: 'center' }}>
                <span className="material-symbols-outlined" style={{ fontSize: 18, color: s.color }}>{s.icon}</span>
                <div style={{ fontSize: 28, fontWeight: 700, color: s.color, lineHeight: 1 }}>{s.value}</div>
                <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--on-surface)' }}>{s.label}</div>
                <div style={{ fontSize: 10, color: 'var(--on-surface-variant)' }}>{s.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alert banner */}
      <div className="alert alert-danger mb-4" style={{ borderRadius: 8, display: 'flex', gap: 12, alignItems: 'flex-start' }}>
        <span className="material-symbols-outlined animate-pulse" style={{ color: 'var(--danger)', fontSize: 20, flexShrink: 0 }}>notification_important</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--danger)', marginBottom: 2 }}>Immediate Phera Threat 🔔 45 mins overdue</div>
          <div style={{ fontSize: 12, color: 'var(--on-surface)', lineHeight: 1.5 }}>Floral decorators expected 7:30 AM, not arrived at Jagmandir Jetty. <strong>Responsible: Priya Sharma</strong><br />Vedic wood mandap needs 3.5h for fresh rajnigandha wrapping prior to 11:30 AM preliminary rituals.</div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          <button className="btn-primary" id="call-vendor-btn" style={{ fontSize: 12, padding: '6px 12px' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 14 }}>call</span>
            Call Vendor (Rathore Florals)
          </button>
          <button className="btn-ghost" style={{ fontSize: 12 }}>+ Reassign Protocol</button>
        </div>
      </div>

      {/* Filter strip */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 10 }}>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', alignSelf: 'center' }}>Filter Status:</span>
          {['All (11)', 'Late (1)', 'Pending (8)', 'Arrived (2)'].map((f, i) => (
            <button key={f} className={`filter-tab${i === 0 ? ' active' : ''}`} style={{ fontSize: 11 }}>{f}</button>
          ))}
        </div>
        <div style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Lead Planner: All Planners (5)</div>
      </div>

      {/* Timeline */}
      <div>
        {TIMELINE_EVENTS.map((ev, idx) => {
          const s = STATUS_MAP[ev.status]
          const isLast = idx === TIMELINE_EVENTS.length - 1

          return (
            <div key={idx} className="timeline-item" style={{ marginBottom: isLast ? 0 : 0 }}>
              {/* Time */}
              <div className="timeline-time" style={{ whiteSpace: 'pre-line', color: ev.status === 'gold' ? 'var(--gold)' : ev.status === 'late' ? 'var(--danger)' : undefined }}>{ev.time}</div>

              {/* Connector */}
              <div className="timeline-connector">
                <div className={`timeline-dot${s.dot ? ' ' + s.dot : ''}`} style={{ background: ev.status === 'pending' ? 'white' : undefined }} />
                {!isLast && <div className="timeline-line" />}
              </div>

              {/* Content card */}
              <div className="timeline-content">
                <div
                  className="card"
                  style={{
                    padding: 14,
                    borderColor: ev.isGolden ? 'rgba(201,162,75,0.4)' : ev.status === 'late' ? 'rgba(198,40,40,0.3)' : undefined,
                    background: ev.isGolden ? 'rgba(201,162,75,0.04)' : undefined,
                  }}
                >
                  {ev.isGolden && (
                    <div className="badge badge-gold mb-2" style={{ fontSize: 11 }}>
                      <span className="material-symbols-outlined" style={{ fontSize: 12 }}>brightness_5</span>
                      Golden Auspicious Window: 17:45 – 18:22 IST &nbsp; Godhuli Muhurat
                    </div>
                  )}
                  {ev.alert && !ev.isGolden && (
                    <div className="badge badge-danger mb-2" style={{ fontSize: 11 }}>
                      <span className="material-symbols-outlined" style={{ fontSize: 12 }}>warning</span>
                      {ev.alert}
                    </div>
                  )}
                  {/* Status + location */}
                  <div style={{ display: 'flex', gap: 8, marginBottom: 4, alignItems: 'center' }}>
                    <span className="material-symbols-outlined" style={{ fontSize: 14, color: s.color }}>{s.icon}</span>
                    <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: s.color }}>{s.label}</span>
                    <span style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>• {ev.location}</span>
                  </div>

                  {/* Title */}
                  <div style={{ fontFamily: "'Playfair Display', serif", fontSize: 17, fontWeight: 700, color: 'var(--on-surface)', marginBottom: 4, lineHeight: 1.3 }}>{ev.title}</div>

                  {/* Desc */}
                  <p style={{ fontSize: 12, color: 'var(--on-surface-variant)', lineHeight: 1.55, marginBottom: 10 }}>{ev.desc}</p>

                  {/* Staff / vendor row */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <div style={{ display: 'flex', gap: 12, fontSize: 11, color: 'var(--on-surface-variant)', flexWrap: 'wrap' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 12 }}>person</span>
                        Planner: {ev.planner}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span className="material-symbols-outlined" style={{ fontSize: 12 }}>store</span>
                        Vendor: {ev.vendor}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: 6 }}>
                      {ev.actions
                        ? ev.actions.map(a => (
                          <button key={a} className="btn-primary" style={{ fontSize: 11, padding: '5px 10px' }} id={`${a.toLowerCase().replace(/ /g,'-')}-btn`}>{a}</button>
                        ))
                        : ev.status !== 'done' && ev.status !== 'in-progress' && (
                          <button className="btn-secondary" style={{ fontSize: 11, padding: '5px 10px' }} id={`mark-arrived-${idx}-btn`}>✓ Mark Arrived</button>
                        )
                      }
                      {ev.logged && <span style={{ fontSize: 11, color: 'var(--success)', alignSelf: 'center' }}>✓ {ev.logged}</span>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
