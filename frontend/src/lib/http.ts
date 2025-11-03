// src/lib/http.ts
/**
 * Tiny HTTP helper for AgroForgeSIM
 * - Uses VITE_API_BASE if the path is relative
 * - Returns parsed JSON or throws a descriptive error
 */

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

const API_BASE = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";

/** Build absolute URL from a relative or absolute input */
function toUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path; // already absolute
  // allow paths with or without leading slash
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${p}`;
}

/** Core request */
async function request<T = unknown>(
  path: string,
  options: RequestInit = {},
  method: HttpMethod = "GET",
): Promise<T> {
  const url = toUrl(path);
  const init: RequestInit = {
    method,
    headers: {
      ...(options.headers || {}),
    },
    ...options,
  };

  // Default JSON headers for non-GET methods when body is present
  if (init.body && !("Content-Type" in (init.headers as Record<string, string>))) {
    (init.headers as Record<string, string>)["Content-Type"] = "application/json";
  }

  const res = await fetch(url, init);

  // Try to parse text first so we can include it in errors if not JSON
  const text = await res.text();
  const contentType = res.headers.get("content-type") || "";

  let data: any = text;
  if (contentType.includes("application/json") || text.startsWith("{") || text.startsWith("[")) {
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      // leave as raw text if JSON parse fails
    }
  }

  if (!res.ok) {
    const detail = typeof data === "string" ? data : JSON.stringify(data);
    throw new Error(`${res.status} ${res.statusText} :: ${detail || "Request failed"}`);
  }

  return data as T;
}

/** Public helpers (named exports) */
export async function getJSON<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, init, "GET");
}

export async function postJSON<T = unknown, B = unknown>(
  path: string,
  body?: B,
  init?: RequestInit,
): Promise<T> {
  return request<T>(
    path,
    { ...init, body: body != null ? JSON.stringify(body) : undefined },
    "POST",
  );
}

export async function putJSON<T = unknown, B = unknown>(
  path: string,
  body?: B,
  init?: RequestInit,
): Promise<T> {
  return request<T>(
    path,
    { ...init, body: body != null ? JSON.stringify(body) : undefined },
    "PUT",
  );
}

export async function patchJSON<T = unknown, B = unknown>(
  path: string,
  body?: B,
  init?: RequestInit,
): Promise<T> {
  return request<T>(
    path,
    { ...init, body: body != null ? JSON.stringify(body) : undefined },
    "PATCH",
  );
}

export async function deleteJSON<T = unknown>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  return request<T>(path, init, "DELETE");
}

/** Utility to build query strings easily */
export function qs(params: Record<string, any>): string {
  const search = new URLSearchParams();
  Object.entries(params || {}).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    if (Array.isArray(v)) v.forEach((item) => search.append(k, String(item)));
    else search.append(k, String(v));
  });
  const s = search.toString();
  return s ? `?${s}` : "";
}
