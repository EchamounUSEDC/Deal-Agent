import {useEffect, useState} from 'react';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

/**
 * Checks whether a file exists under public/ so scenes can fall back to a
 * branded placeholder instead of failing the render when b-roll, audio, or
 * the logo has not been supplied yet.
 *
 * Returns `null` while checking, then `true`/`false`.
 */
export const useAssetExists = (relativePath: string): boolean | null => {
  const [exists, setExists] = useState<boolean | null>(null);
  const [handle] = useState(() =>
    delayRender(`Checking asset availability: ${relativePath}`),
  );

  useEffect(() => {
    let cancelled = false;
    fetch(staticFile(relativePath), {method: 'HEAD'})
      .then((res) => {
        if (!cancelled) {
          setExists(res.ok);
        }
        continueRender(handle);
      })
      .catch((err) => {
        if (!cancelled) {
          setExists(false);
        }
        // A network-level failure still means "asset unavailable" — never
        // fail the render over a missing optional asset.
        if (err instanceof Error && err.name === 'AbortError') {
          cancelRender(err);
        } else {
          continueRender(handle);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [relativePath, handle]);

  return exists;
};
