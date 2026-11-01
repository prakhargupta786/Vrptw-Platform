import { forwardRef, type InputHTMLAttributes } from 'react';

interface Props extends InputHTMLAttributes<HTMLInputElement> { label?: string; error?: string }

export const Input = forwardRef<HTMLInputElement, Props>(({ label, error, className = '', ...props }, ref) => (
  <label className="block text-sm">
    {label && <span className="mb-1 block font-medium text-gray-700">{label}</span>}
    <input ref={ref} className={`w-full rounded-md border border-gray-300 px-3 py-1.5 ${className}`} {...props} />
    {error && <span className="mt-1 block text-xs text-red-600">{error}</span>}
  </label>
));
Input.displayName = 'Input';
