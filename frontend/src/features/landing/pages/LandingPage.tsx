import { Link } from 'react-router-dom';

import { ROUTES } from '@/constants/routes';

const FEATURES = [
  {
    title: 'Plan smarter routes',
    description: 'Build delivery plans that account for vehicle capacity and customer time windows.',
  },
  {
    title: 'Track every run',
    description: 'Follow planning runs from start to finish and review their status in one place.',
  },
  {
    title: 'Measure outcomes',
    description: 'Explore delivery performance, route results, and operational metrics.',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="border-b border-gray-200">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4" aria-label="Main navigation">
          <Link to={ROUTES.landing} className="text-lg font-semibold tracking-tight">VRPTW Planner</Link>
          <Link to={ROUTES.login} className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700">
            Log in
          </Link>
        </nav>
      </header>

      <main>
        <section className="bg-gray-50 px-6 py-20 sm:py-28">
          <div className="mx-auto max-w-6xl">
            <p className="text-sm font-semibold uppercase tracking-widest text-blue-700">Delivery planning, made clear</p>
            <h1 className="mt-4 max-w-3xl text-4xl font-bold tracking-tight sm:text-6xl">
              Better routes start with a better plan.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-600">
              Plan vehicle routes around real-world time windows, manage delivery runs, and understand performance from one workspace.
            </p>
            <Link to={ROUTES.login} className="mt-8 inline-block rounded-md bg-blue-600 px-5 py-3 text-sm font-medium text-white hover:bg-blue-700">
              Log in to your workspace
            </Link>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-6 py-16 sm:py-20" aria-labelledby="features-heading">
          <h2 id="features-heading" className="text-2xl font-semibold tracking-tight">Everything you need to plan with confidence</h2>
          <div className="mt-8 grid gap-6 md:grid-cols-3">
            {FEATURES.map((feature) => (
              <article key={feature.title} className="rounded-lg border border-gray-200 p-6">
                <h3 className="font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm leading-6 text-gray-600">{feature.description}</p>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
