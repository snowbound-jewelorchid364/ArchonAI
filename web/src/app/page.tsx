import Link from "next/link";

const FEATURES = [
  { title: "6 Specialist Agents", desc: "Software, Cloud, Security, Data, Integration, and AI architects working in parallel" },
  { title: "Cited Findings", desc: "Every critical finding backed by code evidence or web sources with full citations" },
  { title: "Under 60 Minutes", desc: "Complete architecture review package delivered faster than any consultant" },
  { title: "14 Modes", desc: "Review, Design, Migration, Compliance, Due Diligence, Incident Response, and more" },
];

const PRICING = [
  { name: "Starter", price: "$49", period: "/mo", features: ["3 reviews/month", "All 6 agents", "Markdown export"], cta: "Start Free Trial" },
  { name: "Pro", price: "$199", period: "/mo", features: ["Unlimited reviews", "PR Reviewer", "ZIP package export", "Priority support"], cta: "Start Pro", highlight: true },
  { name: "Team", price: "$499", period: "/mo", features: ["Everything in Pro", "5 team seats", "Drift Monitor", "Custom modes"], cta: "Contact Sales" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="bg-archon-900 text-white">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <span className="text-2xl font-bold tracking-tight">ARCHON</span>
          <div className="flex items-center gap-6">
            <Link href="/sign-in" className="text-sm text-gray-300 hover:text-white">Sign In</Link>
            <Link href="/sign-up" className="rounded-lg bg-archon-500 px-4 py-2 text-sm font-medium hover:bg-archon-600">
              Get Started
            </Link>
          </div>
        </nav>
        <div className="mx-auto max-w-4xl px-6 py-24 text-center">
          <h1 className="text-5xl font-bold leading-tight">
            Your Frontier AI Architect.
            <br />
            <span className="text-archon-500">From idea to infrastructure.</span>
          </h1>
          <p className="mt-6 text-lg text-gray-300">
            6 specialist AI agents audit your codebase in parallel. Get a complete architecture
            review package with findings, ADRs, IaC skeletons, and risk register — in under an hour.
          </p>
          <div className="mt-10 flex justify-center gap-4">
            <Link href="/sign-up" className="rounded-lg bg-archon-500 px-8 py-3 text-lg font-semibold hover:bg-archon-600">
              Start Free Review
            </Link>
            <Link href="#pricing" className="rounded-lg border border-gray-600 px-8 py-3 text-lg hover:bg-gray-800">
              View Pricing
            </Link>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-24">
        <h2 className="text-center text-3xl font-bold">Why ARCHON?</h2>
        <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <div key={f.title} className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-archon-700">{f.title}</h3>
              <p className="mt-2 text-sm text-gray-600">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="bg-gray-100 px-6 py-24">
        <h2 className="text-center text-3xl font-bold">Simple Pricing</h2>
        <div className="mx-auto mt-12 grid max-w-5xl gap-8 md:grid-cols-3">
          {PRICING.map((p) => (
            <div
              key={p.name}
              className={`rounded-xl border bg-white p-8 shadow-sm ${p.highlight ? "border-archon-500 ring-2 ring-archon-500" : "border-gray-200"}`}
            >
              <h3 className="text-xl font-semibold">{p.name}</h3>
              <div className="mt-4">
                <span className="text-4xl font-bold">{p.price}</span>
                <span className="text-gray-500">{p.period}</span>
              </div>
              <ul className="mt-6 space-y-3">
                {p.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm text-gray-700">
                    <span className="text-archon-500">✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/sign-up"
                className={`mt-8 block rounded-lg py-3 text-center text-sm font-semibold ${
                  p.highlight
                    ? "bg-archon-500 text-white hover:bg-archon-600"
                    : "border border-gray-300 text-gray-700 hover:bg-gray-50"
                }`}
              >
                {p.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-archon-900 px-6 py-12 text-center text-sm text-gray-400">
        © 2026 ARCHON. All rights reserved.
      </footer>
    </div>
  );
}
