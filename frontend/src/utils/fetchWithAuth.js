export async function fetchWithAuth(url, options = {}, retry = true) {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');

  const headers = {
    ...options.headers,
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401 && retry && refreshToken) {
      // Versuch Access Token zu aktualisieren
      const refreshRes = await fetch('http://127.0.0.1:8000/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (refreshRes.ok) {
        const newTokens = await refreshRes.json();
        localStorage.setItem('accessToken', newTokens.access);

        // 🌀 Zweiter Versuch mit neuem Token
        return fetchWithAuth(url, options, false);
      } else {
        // Refresh fehlgeschlagen → logout
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return;
      }
    }

    return response;
  } catch (err) {
    console.error('❌ Network error:', err);
    throw err;
  }
}