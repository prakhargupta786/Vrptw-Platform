import { create } from 'zustand';

interface RunState {
  runId: string | null;
  setRunId: (id: string | null) => void;
}

export const useRunStore = create<RunState>((set) => ({
  runId: null,
  setRunId: (runId) => set({ runId }),
}));
