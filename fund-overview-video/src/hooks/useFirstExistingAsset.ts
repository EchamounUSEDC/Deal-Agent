import {useEffect, useMemo, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

/**
 * Given an ordered list of candidate files under public/, resolves to the
 * first one that exists. Resolves to `false` when none exist (callers show
 * a placeholder), `null` while checking.
 *
 * Lets scenes prefer dedicated footage (e.g. assets/broll/production.mp4)
 * while gracefully reusing the primary rig b-roll when it is absent.
 */
export const useFirstExistingAsset = (
  candidates: string[],
): string | false | null => {
  const key = candidates.join('|');
  const list = useMemo(() => candidates, [key]); // eslint-disable-line react-hooks/exhaustive-deps
  const [resolved, setResolved] = useState<string | false | null>(null);
  const [handle] = useState(() =>
    delayRender(`Resolving footage candidates: ${key}`),
  );

  useEffect(() => {
    let cancelled = false;
    (async () => {
      for (const candidate of list) {
        try {
          const res = await fetch(staticFile(candidate), {method: 'HEAD'});
          if (res.ok) {
            if (!cancelled) {
              setResolved(candidate);
            }
            continueRender(handle);
            return;
          }
        } catch {
          // Treat network errors as "not available" and keep checking.
        }
      }
      if (!cancelled) {
        setResolved(false);
      }
      continueRender(handle);
    })();
    return () => {
      cancelled = true;
    };
  }, [list, handle]);

  return resolved;
};
