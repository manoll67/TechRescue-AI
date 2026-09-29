export const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
    }
}

export async function apiFetch(path, { method = 'GET', body, token } = {}) {
    let response;

    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            method,
            headers: {
                ...(body ? { 'Content-Type': 'application/json' } : {}),
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: body ? JSON.stringify(body) : undefined,
        });
    } catch {
        throw new ApiError('Няма връзка със сървъра.', 0);
    }

    if (response.status === 204) {
        return null;
    }

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = payload && typeof payload.detail === 'string' ? payload.detail : null;
        throw new ApiError(detail || `Грешка от сървъра (${response.status}).`, response.status);
    }

    return payload;
}
