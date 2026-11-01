import { useState } from 'react';

export function usePagination(initialSize = 50) {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialSize);
  return { page, pageSize, setPage, setPageSize, query: { page, page_size: pageSize } };
}
