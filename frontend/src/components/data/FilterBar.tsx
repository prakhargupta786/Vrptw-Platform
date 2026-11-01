export interface FilterDef { key: string; label: string; options: string[] }

export function FilterBar({ filters, values, onChange }: {
  filters: FilterDef[]; values: Record<string, string | undefined>; onChange: (key: string, value: string | undefined) => void;
}) {
  return (
    <div className="mb-3 flex flex-wrap gap-2">
      {filters.map((f) => (
        <select key={f.key} className="rounded-md border border-gray-300 px-2 py-1 text-sm" value={values[f.key] ?? ''}
          onChange={(e) => onChange(f.key, e.target.value || undefined)}>
          <option value="">{f.label}: all</option>
          {f.options.map((o) => <option key={o} value={o}>{o}</option>)}
        </select>
      ))}
    </div>
  );
}
