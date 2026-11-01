import { useParams } from 'react-router-dom';

/** Run id from the /r/:runId/... URL. Pages under /r/ are only mounted when it exists. */
export function useRunId(): string {
  const { runId } = useParams();
  if (!runId) throw new Error('useRunId used outside /r/:runId routes');
  return runId;
}
