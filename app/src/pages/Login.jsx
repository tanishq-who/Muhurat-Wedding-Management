import { useState } from 'react'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('aryan.rathore@royalknot.in')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [remember, setRemember] = useState(true)
  const [error, setError] = useState(true)
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setLoading(true)
    setError(false)
    setTimeout(() => {
      setLoading(false)
      // Accept any credentials for demo
      if (email && password) {
        onLogin()
      } else {
        setError(true)
      }
    }, 900)
  }

  const autoFill = () => {
    setEmail('pooja.rathore@royalknot.in')
    setPassword('RambaghMuhurat2025')
    setError(false)
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--primary-container)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px 16px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background mandala watermark */}
      <svg
        style={{ position: 'absolute', width: 900, height: 900, opacity: 0.04, pointerEvents: 'none', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}
        viewBox="0 0 800 800" fill="none" stroke="var(--secondary-fixed)" strokeWidth="1.2"
      >
        <circle cx="400" cy="400" r="380" strokeDasharray="4 8" />
        <circle cx="400" cy="400" r="320" strokeWidth="0.8" />
        <circle cx="400" cy="400" r="260" strokeDasharray="3 6" />
        <circle cx="400" cy="400" r="200" />
        <circle cx="400" cy="400" r="140" />
        <path d="M400 20 L400 780 M20 400 L780 400 M131 131 L669 669 M131 669 L669 131" strokeWidth="0.75" />
        <polygon points="400,100 480,260 640,260 510,360 560,510 400,420 240,510 290,360 160,260 320,260" />
      </svg>

      {/* Glow blobs */}
      <div style={{ position: 'absolute', width: 600, height: 600, borderRadius: '50%', background: 'rgba(253,210,117,0.07)', filter: 'blur(100px)', top: -100, left: '50%', transform: 'translateX(-50%)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', width: 500, height: 500, borderRadius: '50%', background: 'rgba(93,3,37,0.35)', filter: 'blur(90px)', bottom: -50, left: '50%', transform: 'translateX(-50%)', pointerEvents: 'none' }} />

      {/* Content */}
      <div style={{ position: 'relative', zIndex: 10, width: '100%', maxWidth: 460, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {/* Brand header */}
        <header style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, padding: '4px 14px', borderRadius: 9999, background: 'rgba(93,3,37,0.5)', marginBottom: 12 }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--secondary-container)', display: 'inline-block', animation: 'pulse 2s infinite' }} />
            <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--secondary-fixed)' }}>The Royal Knot • Jaipur • Udaipur</span>
          </div>
          <h1 style={{ fontFamily: "'Playfair Display', serif", fontSize: 'clamp(36px, 8vw, 56px)', fontWeight: 700, color: 'var(--secondary-fixed)', letterSpacing: '-0.02em', lineHeight: 1 }}>
            Muhurat
          </h1>
          <p style={{ fontFamily: "'Playfair Display', serif", fontSize: 18, fontStyle: 'italic', color: 'var(--tertiary-fixed)', opacity: 0.9, marginTop: 6 }}>
            Every Perfect Wedding Begins Here.
          </p>
        </header>

        {/* Card */}
        <div style={{ width: '100%', background: 'var(--surface-container-lowest)', borderRadius: 12, boxShadow: '0 24px 64px rgba(0,0,0,0.25)', overflow: 'hidden' }}>
          {/* Gold strip */}
          <div style={{ height: 4, background: 'linear-gradient(90deg, var(--secondary), var(--secondary-container), var(--secondary))' }} />

          <div style={{ padding: '28px 28px 0' }}>
            {/* Card header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
              <div>
                <h2 style={{ fontFamily: "'Playfair Display', serif", fontSize: 22, fontWeight: 700, color: 'var(--on-surface)' }}>Agency Access Portal</h2>
                <p style={{ fontSize: 13, color: 'var(--on-surface-variant)', marginTop: 4 }}>Enter your royal planner credentials to manage wedding itineraries.</p>
              </div>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--surface-container)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 16, color: 'var(--secondary)' }}>verified_user</span>
              </div>
            </div>

            {/* Error alert */}
            {error && (
              <div className="alert alert-error" style={{ marginBottom: 16 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 18, color: 'var(--error)', flexShrink: 0 }}>error</span>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: 12, color: 'var(--error)' }}>Access Restricted</div>
                  <div style={{ fontSize: 12, marginTop: 2 }}>Invalid credentials. Please verify your agency email or password.</div>
                </div>
                <button onClick={() => setError(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--on-surface-variant)', flexShrink: 0 }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 16 }}>close</span>
                </button>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {/* Email */}
              <div className="form-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label className="form-label" htmlFor="login-email">Username or Agency Email</label>
                  <span style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>Jaipur HQ Staff</span>
                </div>
                <div className="form-input-icon">
                  <span className="material-symbols-outlined form-input-icon-el">mail</span>
                  <input
                    id="login-email"
                    className="form-input"
                    type="email"
                    required
                    placeholder="e.g. aryan.rathore@royalknot.in"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                  />
                </div>
              </div>

              {/* Password */}
              <div className="form-group">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label className="form-label" htmlFor="login-password">Security Password</label>
                  <button
                    type="button"
                    onClick={() => alert('Password reset link sent to your registered mobile.')}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 11, color: 'var(--secondary)', fontWeight: 600 }}
                  >
                    Forgot password?
                  </button>
                </div>
                <div className="form-input-icon" style={{ position: 'relative' }}>
                  <span className="material-symbols-outlined form-input-icon-el">lock</span>
                  <input
                    id="login-password"
                    className="form-input"
                    type={showPassword ? 'text' : 'password'}
                    required
                    placeholder="Enter account security key"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    style={{ paddingRight: 42 }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(p => !p)}
                    style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--on-surface-variant)' }}
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: 18 }}>{showPassword ? 'visibility_off' : 'visibility'}</span>
                  </button>
                </div>
              </div>

              {/* Remember */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
                  <div
                    onClick={() => setRemember(r => !r)}
                    style={{
                      width: 18, height: 18, borderRadius: 4,
                      background: remember ? 'var(--primary-container)' : 'var(--surface)',
                      border: remember ? 'none' : '1.5px solid var(--outline-variant)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      cursor: 'pointer', flexShrink: 0, transition: 'all 0.18s',
                    }}
                  >
                    {remember && <span className="material-symbols-outlined" style={{ fontSize: 13, color: 'white' }}>check</span>}
                  </div>
                  <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Remember this device for 30 days</span>
                </label>
                <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 9999, background: 'rgba(253,210,117,0.3)', color: 'var(--on-secondary-container)' }}>
                  Station Safe
                </span>
              </div>

              {/* Submit */}
              <button
                id="login-submit-btn"
                type="submit"
                disabled={loading}
                style={{
                  width: '100%', padding: '12px 16px', borderRadius: 8, border: 'none',
                  background: loading ? 'var(--surface-container-high)' : 'var(--primary-container)',
                  color: loading ? 'var(--on-surface-variant)' : 'white',
                  fontWeight: 700, fontSize: 15, cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  fontFamily: "'Inter', sans-serif", transition: 'all 0.18s',
                  letterSpacing: '0.02em',
                }}
              >
                {loading
                  ? <><span className="material-symbols-outlined animate-spin" style={{ fontSize: 18 }}>progress_activity</span> Authenticating…</>
                  : <><span>Sign In to Executive Deck</span><span className="material-symbols-outlined" style={{ fontSize: 18 }}>arrow_forward</span></>
                }
              </button>
            </form>

            {/* Divider */}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '20px 0' }}>
              <div style={{ position: 'absolute', left: 0, right: 0, height: 1, background: 'var(--surface-container-high)' }} />
              <div style={{ position: 'relative', background: 'var(--surface-container-lowest)', padding: '0 12px', display: 'flex', alignItems: 'center', gap: 6 }}>
                <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>auto_awesome</span>
                <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--on-surface-variant)' }}>Udaipur • Rambagh • Umaid</span>
                <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>auto_awesome</span>
              </div>
            </div>

            {/* Quick-fill profile */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 14px', background: 'var(--surface-container-low)', borderRadius: 8, marginBottom: 28 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'var(--primary-fixed)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 12, color: 'var(--primary-container)' }}>PR</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--on-surface)' }}>Pooja Rathore</div>
                  <div style={{ fontSize: 11, color: 'var(--on-surface-variant)' }}>Senior Muhurat Connoisseur</div>
                </div>
              </div>
              <button
                type="button"
                onClick={autoFill}
                style={{ padding: '5px 12px', borderRadius: 6, background: 'var(--surface-container)', border: '1px solid var(--beige-border)', fontSize: 12, fontWeight: 600, color: 'var(--primary-container)', cursor: 'pointer', fontFamily: "'Inter', sans-serif" }}
              >
                Quick Fill
              </button>
            </div>
          </div>

          {/* Card footer */}
          <div style={{ background: 'var(--surface-container-low)', padding: '12px 28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--on-surface-variant)' }}>
              <span className="material-symbols-outlined" style={{ fontSize: 14, color: 'var(--secondary)' }}>shield_lock</span>
              256-bit Royal Encryption
            </div>
            <span style={{ fontSize: 11, color: 'var(--on-surface-variant)', opacity: 0.7 }}>Muhurat OS v2.4</span>
          </div>
        </div>

        {/* Footer */}
        <footer style={{ marginTop: 24, textAlign: 'center' }}>
          <p style={{ fontSize: 12, color: 'var(--tertiary-fixed)', opacity: 0.85 }}>Need VIP planner access or token renewal?</p>
          <a href="mailto:it-support@royalknot.in" style={{ fontSize: 12, color: 'var(--secondary-fixed)', textDecoration: 'underline', display: 'inline-flex', alignItems: 'center', gap: 4, marginTop: 4 }}>
            Contact Jaipur Central HQ (it-support@royalknot.in)
            <span className="material-symbols-outlined" style={{ fontSize: 12 }}>north_east</span>
          </a>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 8, fontSize: 11, color: 'rgba(236,225,203,0.5)' }}>
            <span>Privacy Charter</span><span>•</span><span>Courtly Protocol</span><span>•</span><span>Muhurat Astrological Desk</span>
          </div>
        </footer>
      </div>
    </div>
  )
}
