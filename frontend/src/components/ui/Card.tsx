import type { ReactNode } from 'react';

export function Card({ title, actions, children }: { title?: string; actions?: ReactNode; children: ReactNode }) {
  return (
    <section className="rounded-lg border border-gray-200 bg-white p-4">
      {(title || actions) && (
        <header className="mb-3 flex items-center justify-between">
          {title && <h2 className="font-semibold">{title}</h2>}
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}
