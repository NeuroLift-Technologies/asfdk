import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { Ajv } from 'ajv';

const schemaPath = fileURLToPath(new URL(
  '../../schemas/toi-1.0.0.schema.json',
  import.meta.url,
));

let validatorPromise: Promise<ReturnType<Ajv['getSchema']>> | undefined;

async function getValidator() {
  if (!validatorPromise) {
    validatorPromise = readFile(schemaPath, 'utf-8')
      .then((raw) => {
        const schema = JSON.parse(raw) as object;
        const ajv = new Ajv({ allErrors: true, strict: false, validateSchema: false });
        ajv.addSchema(schema, 'toi');
        return ajv.getSchema('toi');
      })
      .catch((err) => {
        validatorPromise = undefined;
        throw err;
      });
  }
  return validatorPromise;
}

/** Result of a TOI v1.0.0 schema validation. */
export interface TOIValidationResult {
  valid: boolean;
  errors?: Array<{
    message: string;
    instancePath: string;
    keyword: string;
    schemaPath: string;
  }>;
  toi?: unknown;
}

/**
 * Validates `candidate` against the TOI v1.0.0 JSON Schema.
 * Lazy-loads and caches the AJV validator on first call.
 *
 * @throws {Error} If the schema file cannot be read or parsed.
 */
export async function validateTOI(candidate: unknown): Promise<TOIValidationResult> {
  const validate = await getValidator();
  if (!validate) throw new Error('TOI schema failed to initialize.');
  const valid = validate(candidate);
  if (valid) return { valid: true, toi: candidate };
  return {
    valid: false,
    errors: (validate.errors ?? []).map((e) => ({
      message: e.message ?? 'Unknown validation error',
      instancePath: e.instancePath,
      keyword: e.keyword,
      schemaPath: e.schemaPath,
    })),
  };
}

/** Returns the active TOI-OTOI component status. */
export function getStatus(): { active: boolean; mode: string } {
  return { active: true, mode: 'schema-validation' };
}
