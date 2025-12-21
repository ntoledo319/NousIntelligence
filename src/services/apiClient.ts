/**
 * apiClient
 *
 * Small fetch wrapper with consistent JSON parsing + error surface.
 *
 * @context_boundary Frontend <-> backend HTTP only
 * # AI-GENERATED 2025-12-21
 */
export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(message: string, status: number, payload: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}

export async function requestJson<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const res = await fetch(input, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  const text = await res.text();
  const json = text ? safeJsonParse(text) : null;

  if (!res.ok) {
    const msg =
      (json &&
      typeof json === 'object' &&
      'error' in json &&
      typeof (json as any).error === 'string'
        ? (json as any).error
        : `Request failed (${res.status})`) || `Request failed (${res.status})`;
    throw new ApiError(msg, res.status, json);
  }

  return json as T;
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
