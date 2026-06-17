/** Result returned by the RRT Advocate stub for all crisis assessments. */
export interface RRTAssessment {
  supported: false;
  reason: string;
}

/**
 * RRT Advocate crisis detection is Python-only in this release.
 *
 * Always returns `{ supported: false }`. Use the Python `asfdk` package for full
 * crisis-detection functionality. TypeScript RRT support is planned for a future release.
 */
export function assess(_input: string): RRTAssessment {
  return {
    supported: false,
    reason: 'Use Python asfdk for crisis detection. TypeScript RRT support is planned for a future release.',
  };
}

/** Returns the static RRT Advocate stub status. Always inactive in the TypeScript package. */
export function getStatus(): { active: boolean; mode: string } {
  return { active: false, mode: 'stub-python-only' };
}
