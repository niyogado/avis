import { useEffect, useState } from 'react';

export function useApiState(apiCall, deps = []) {
  const [state, setState] = useState({
    loading: true,
    data: null,
    error: null,
    empty: false,
  });

  useEffect(() => {
    let mounted = true;
    async function run() {
      setState({ loading: true, data: null, error: null, empty: false });
      try {
        const data = await apiCall();
        if (!mounted) return;
        const isEmpty = data == null || (Array.isArray(data) && data.length === 0);
        setState({ loading: false, data: data, error: null, empty: isEmpty });
      } catch (err) {
        if (!mounted) return;
        setState({ loading: false, data: null, error: err, empty: false });
      }
    }
    run();
    return () => (mounted = false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
