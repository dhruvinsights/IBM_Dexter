import { useEffect, useState } from 'react';

/**
 * Cycles through phrases with a typing effect. Phrases should be stable (memoized) across renders.
 */
export function useTypewriter(phrases, { typingMs = 42, pauseMs = 2600 } = {}) {
  const [display, setDisplay] = useState('');
  const [phraseIndex, setPhraseIndex] = useState(0);

  useEffect(() => {
    if (!phrases?.length) {
      const clearId = window.setTimeout(() => setDisplay(''), 0);
      return () => window.clearTimeout(clearId);
    }

    const phrase = phrases[phraseIndex % phrases.length];
    let char = 0;
    let timeoutId;

    const tick = () => {
      char += 1;
      setDisplay(phrase.slice(0, char));
      if (char < phrase.length) {
        timeoutId = window.setTimeout(tick, typingMs);
      } else {
        timeoutId = window.setTimeout(() => {
          setPhraseIndex((i) => i + 1);
        }, pauseMs);
      }
    };

    const startId = window.setTimeout(() => {
      setDisplay('');
      timeoutId = window.setTimeout(tick, typingMs);
    }, 0);

    return () => {
      window.clearTimeout(startId);
      window.clearTimeout(timeoutId);
    };
  }, [phraseIndex, phrases, typingMs, pauseMs]);

  return display;
}
