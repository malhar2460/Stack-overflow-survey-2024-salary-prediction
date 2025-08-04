const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchModelSchema() {
  const res = await fetch(`${API_BASE_URL}/api/v1/model-schema`);
  return res.json();
}
