export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-10 sm:px-12">
      <header className="flex items-center justify-between border-b border-emerald-900/15 pb-6">
        <span className="text-xl font-bold tracking-tight">AgentPay<span className="text-emerald-600">.</span></span>
        <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-900">Foundation preview</span>
      </header>
      <section className="flex flex-1 flex-col justify-center py-20">
        <p className="mb-6 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">Intent-aware commerce</p>
        <h1 className="max-w-3xl text-5xl font-semibold leading-tight tracking-tight sm:text-7xl">The right purchase starts with understanding.</h1>
        <p className="mt-8 max-w-xl text-lg leading-relaxed text-emerald-950/65">AgentPay is being built to verify that a purchase matches your requirements before payment.</p>
        <div className="mt-12 grid gap-5 border-t border-emerald-900/15 pt-8 sm:grid-cols-3">
          {[
            ["01", "Describe", "Start with what matters to you."],
            ["02", "Verify", "Check requirements against evidence."],
            ["03", "Approve", "Review the purchase before checkout."],
          ].map(([number, title, description]) => (
            <div key={number}>
              <span className="text-xs font-mono text-emerald-700">{number} / Planned</span>
              <h2 className="mt-3 text-lg font-semibold">{title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-emerald-950/65">{description}</p>
            </div>
          ))}
        </div>
      </section>
      <footer className="border-t border-emerald-900/15 pt-6 text-sm text-emerald-950/60">Scaffold preview · Purchase and checkout features are coming in later stages.</footer>
    </main>
  );
}
