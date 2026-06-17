export interface RRTAssessment {
  supported: false;
  reason: string;
}

// RRT Advocate crisis detection is Python-only in this release.
// Use the Python asfdk package for full RRT functionality.
export function assess(_input: string): RRTAssessment {
  return {
    supported: false,
    reason: 'Use Python asfdk for crisis detection. TypeScript RRT support is planned for a future release.',
  };
}

export function getStatus(): { active: boolean; mode: string } {
  return { active: false, mode: 'stub-python-only' };
}
