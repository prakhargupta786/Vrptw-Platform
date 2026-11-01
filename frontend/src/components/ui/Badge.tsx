const tone: Record<string, string> = {
  green: 'bg-green-100 text-green-800', red: 'bg-red-100 text-red-800', amber: 'bg-amber-100 text-amber-800',
  blue: 'bg-blue-100 text-blue-800', gray: 'bg-gray-100 text-gray-700',
};
const STATUS_TONE: Record<string, keyof typeof tone> = {
  delivered: 'green', pass: 'green', validated: 'green', succeeded: 'green', assigned: 'blue', ready: 'blue',
  late: 'amber', generating: 'amber', validating: 'amber', running: 'amber', soft: 'amber',
  failed: 'red', fail: 'red', unserved: 'red', cancelled: 'red', locked: 'gray',
};

export function Badge({ value }: { value: string }) {
  return <span className={`rounded px-2 py-0.5 text-xs font-medium ${tone[STATUS_TONE[value] ?? 'gray']}`}>{value}</span>;
}
