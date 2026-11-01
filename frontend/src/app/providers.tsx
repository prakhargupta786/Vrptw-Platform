import { QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState, type ReactNode } from 'react';

import { Spinner } from '@/components/ui';
import { refreshAccessToken } from '@/lib/http';
import { queryClient } from '@/lib/queryClient';

/** Access token lives in memory, so on page load we restore the session from the httpOnly refresh cookie. */
function SessionBootstrap({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  useEffect(() => { refreshAccessToken().finally(() => setReady(true)); }, []);
  return ready ? <>{children}</> : <Spinner />;
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <SessionBootstrap>{children}</SessionBootstrap>
    </QueryClientProvider>
  );
}
