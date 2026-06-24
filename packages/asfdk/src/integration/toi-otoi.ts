import { safeParseToi, ToiValidationError, type ToiDocument } from '@neurolift-technologies/toi';
import { parseCharter, type OtoiCharter } from '@neurolift-technologies/otoi';

/** A single validation issue, flattened to a dotted path and a message. */
export interface ValidationIssue {
  message: string;
  path: string;
  code: string;
}

/** Result of a `.toi` v1.0.0 schema validation. */
export interface TOIValidationResult {
  valid: boolean;
  errors?: ValidationIssue[];
  toi?: ToiDocument;
}

/**
 * Validates `candidate` against the canonical `.toi` v1.0.0 schema using the
 * `@neurolift-technologies/toi` reference implementation (the single source of
 * truth for the format). Non-throwing.
 */
export function validateTOI(candidate: unknown): TOIValidationResult {
  const result = safeParseToi(candidate);
  if (result.success) return { valid: true, toi: result.data };

  const { error } = result;
  if (error instanceof ToiValidationError) {
    return {
      valid: false,
      errors: error.issues.map((issue) => ({
        message: issue.message,
        path: issue.path,
        code: error.code,
      })),
    };
  }
  return { valid: false, errors: [{ message: error.message, path: '', code: error.code }] };
}

/** Result of an `.otoi` charter validation. */
export interface OTOIValidationResult {
  valid: boolean;
  errors?: ValidationIssue[];
  charter?: OtoiCharter;
}

/**
 * Validates `candidate` against the `.otoi` charter schema using the
 * `@neurolift-technologies/otoi` honoring layer. A `.otoi` charter declares how
 * a mesh of agents honors a stack of `.toi` documents at runtime.
 */
export function validateCharter(candidate: unknown): OTOIValidationResult {
  try {
    const charter = parseCharter(candidate);
    return { valid: true, charter };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    const code = (err as { code?: string }).code ?? 'error';
    return { valid: false, errors: [{ message, path: '', code }] };
  }
}

/** Returns the active TOI-OTOI component status. */
export function getStatus(): { active: boolean; mode: string } {
  return { active: true, mode: 'toi-otoi-validation' };
}
