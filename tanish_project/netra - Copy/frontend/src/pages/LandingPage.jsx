import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function LandingPage() {
  const [domain, setDomain] = useState('')
  const navigate = useNavigate()

  const handleScan = (e) => {
    e.preventDefault()
    if (domain) {
      navigate(`/scan?domain=${domain}`)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Navbar */}
      <Navbar />

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl font-bold mb-6">
            <span className="text-gradient">AI-Powered</span> Security Assessment
          </h2>
          <p className="text-xl text-slate-400 mb-4">
            Check your website's security in seconds. No technical knowledge required.
          </p>
          <p className="text-lg text-slate-500 mb-8">
            Simply enter a domain name and NETRA will analyze its security posture, detect vulnerabilities, and provide actionable recommendations.
          </p>
          
          {/* Search Box */}
          <form onSubmit={handleScan} className="max-w-2xl mx-auto">
            <div className="flex gap-4">
              <input
                type="text"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                placeholder="Enter domain (e.g., example.com)"
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition"
              />
              <button
                type="submit"
                className="bg-cyan-500 hover:bg-cyan-600 text-white px-8 py-3 rounded-lg font-semibold transition"
              >
                Scan Now
              </button>
            </div>
            <p className="text-sm text-slate-500 mt-3">
              Free scan • No registration required • Results in seconds
            </p>
          </form>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-5xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-4">How NETRA Works</h3>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            NETRA performs a comprehensive security assessment using only publicly available information. It's completely passive and safe - no active attacks are performed.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-cyan-500">1</span>
              </div>
              <h4 className="text-xl font-semibold mb-2">Enter Domain</h4>
              <p className="text-slate-400">
                Simply type any website domain into the search box. No technical setup required.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-cyan-500">2</span>
              </div>
              <h4 className="text-xl font-semibold mb-2">Automatic Analysis</h4>
              <p className="text-slate-400">
                NETRA checks WHOIS, DNS, SSL certificates, security headers, and email configuration.
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-cyan-500">3</span>
              </div>
              <h4 className="text-xl font-semibold mb-2">Get Results</h4>
              <p className="text-slate-400">
                Receive a detailed security report with risk score, findings, and AI-powered recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-4">What NETRA Checks</h3>
          <p className="text-slate-400 text-center mb-12 max-w-2xl mx-auto">
            NETRA analyzes multiple aspects of your website's security to provide a comprehensive assessment.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: 'WHOIS Analysis', desc: 'Checks domain registration details, expiration date, and registrar information to ensure your domain is properly maintained.', icon: '🔍' },
              { title: 'DNS Configuration', desc: 'Analyzes DNS records including A, MX, NS, and TXT records to ensure proper domain resolution and email delivery.', icon: '🌐' },
              { title: 'SSL Certificate', desc: 'Validates SSL/TLS certificates, checks expiration dates, and verifies proper encryption configuration.', icon: '🔒' },
              { title: 'Security Headers', desc: 'Inspects HTTP security headers like HSTS, CSP, and X-Frame-Options to protect against common web attacks.', icon: '🛡️' },
              { title: 'Email Security', desc: 'Verifies SPF, DKIM, and DMARC records to prevent email spoofing and improve deliverability.', icon: '📧' },
              { title: 'AI-Powered Reports', desc: 'Uses AI to explain findings in simple language and provide actionable recommendations for improvement.', icon: '🤖' },
            ].map((feature, index) => (
              <div key={index} className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-cyan-500 transition">
                <div className="text-3xl mb-3">{feature.icon}</div>
                <h4 className="text-xl font-semibold mb-2 text-gradient">{feature.title}</h4>
                <p className="text-slate-400 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-3xl font-bold mb-4">Why Use NETRA?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
            <div>
              <div className="text-4xl mb-3">⚡</div>
              <h4 className="text-lg font-semibold mb-2">Fast & Easy</h4>
              <p className="text-slate-400 text-sm">
                Get results in seconds. No complex setup or technical knowledge needed.
              </p>
            </div>
            <div>
              <div className="text-4xl mb-3">🔐</div>
              <h4 className="text-lg font-semibold mb-2">Completely Safe</h4>
              <p className="text-slate-400 text-sm">
                Passive analysis only. No active attacks or intrusive scanning.
              </p>
            </div>
            <div>
              <div className="text-4xl mb-3">📊</div>
              <h4 className="text-lg font-semibold mb-2">Detailed Reports</h4>
              <p className="text-slate-400 text-sm">
                Professional security reports with AI-powered explanations and recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h3>
          <div className="space-y-4">
            {[
              {
                q: "Is NETRA safe to use?",
                a: "Yes, NETRA is completely safe. It only analyzes publicly available information and performs no active attacks on your website."
              },
              {
                q: "Do I need to be technical to use NETRA?",
                a: "Not at all. NETRA is designed for everyone. Simply enter a domain and get easy-to-understand results."
              },
              {
                q: "How long does a scan take?",
                a: "Most scans complete within 10-30 seconds, depending on the domain and network conditions."
              },
              {
                q: "What happens with my scan data?",
                a: "Your scan results are stored securely and are only used to provide you with the security assessment."
              },
            ].map((faq, index) => (
              <div key={index} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h4 className="font-semibold mb-2 text-cyan-500">{faq.q}</h4>
                <p className="text-slate-400 text-sm">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 px-4">
        <div className="max-w-7xl mx-auto text-center text-slate-400">
          <p>&copy; 2024 NETRA. AI-Powered Security Assessment Platform.</p>
          <p className="text-sm mt-2">Built for educational purposes. Passive security assessment only.</p>
        </div>
      </footer>
    </div>
  )
}
