/**
 * Thin fetch wrapper.
 * Expects every backend response to have the shape { data: T, meta: {...} }
 * and unwraps the `data` field automatically.
 */
export async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${res.status} ${res.statusText} — ${path}\n${text}`)
  }
  const json = await res.json()
  return json.data as T
}
