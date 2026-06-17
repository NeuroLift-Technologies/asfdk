import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import Ajv from 'ajv';

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

export interface TOIValidationResult {
  valid: boolean;
  errors?: Array<{ message: string; instancePath: string }>;
  toi?: unknown;
}

export async function validateTOI(candidate: unknown): Promise<TOIValidationResult> {
  const validate = await getValidator();
  if (!validate) throw new Error('TOI schema failed to initialize.');
  const valid = validate(candidate) as boolean;
  if (valid) return { valid: true, toi: candidate };
  return {
    valid: false,
    errors: (validate.errors ?? []).map((e) => ({
      message: e.message ?? 'Unknown validation error',
      instancePath: e.instancePath,
    })),
  };
}

export function getStatus(): { active: boolean; mode: string } {
  return { active: true, mode: 'schema-validation' };
}
