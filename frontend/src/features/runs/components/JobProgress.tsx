import { useEffect } from 'react';

import { Badge } from '@/components/ui';
import { useJobPolling } from '@/hooks/useJobPolling';

export function JobProgress({ jobId, onDone }: { jobId: string | null; onDone?: () => void }) {
  const { data: job } = useJobPolling(jobId);
  const succeeded = job?.status === 'succeeded';
  useEffect(() => {
    if (succeeded) onDone?.();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [succeeded]);
  if (!job) return null;
  return (
    <div className="space-y-1 text-sm">
      <div className="flex items-center gap-2"><Badge value={job.status} /><span>{job.kind}{job.step ? ` · ${job.step}` : ''}</span></div>
      <div className="h-2 rounded bg-gray-200"><div className="h-2 rounded bg-blue-600" style={{ width: `${job.progress}%` }} /></div>
      {job.error && <p className="text-red-600">{job.error}</p>}
    </div>
  );
}
