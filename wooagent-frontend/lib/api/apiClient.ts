export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // כאן תוסיף לוגיקת אימות אם נדרש בעתיד
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';
  const fullUrl = `${baseUrl}${url}`;
  
  console.log(`API Request: ${options.method || 'GET'} ${fullUrl}`, 
              options.body ? JSON.parse(options.body as string) : '');
  
  try {
    const response = await fetch(fullUrl, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await response.json();
    
    console.log(`API Response: ${response.status}`, data);

    if (!response.ok) {
      if (data && data.error) {
        throw new ApiError(response.status, data.error || `API error: ${response.status} ${response.statusText}`);
      }
      throw new ApiError(response.status, `API error: ${response.status} ${response.statusText}`);
    }

    // אם תשובת השרת מכילה שדה response, נחזיר אותו ישירות
    if (data && data.response) {
      return data.response;
    }
    
    // אם תשובת השרת מכילה שדה success, נחזיר את שאר המידע
    if (data && typeof data.success === 'boolean') {
      if (!data.success) {
        throw new ApiError(response.status, data.message || 'שגיאה לא ידועה');
      }
      
      // מחזירים את התשובה בלי שדה success
      const { success, ...restData } = data;
      return restData;
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

export const apiClient = {
  get: <T>(path: string): Promise<T> => {
    return fetchWithAuth(path, { method: 'GET' });
  },
  
  post: <T>(path: string, data: any): Promise<T> => {
    return fetchWithAuth(path, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  put: <T>(path: string, data: any): Promise<T> => {
    return fetchWithAuth(path, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  delete: <T>(path: string): Promise<T> => {
    return fetchWithAuth(path, { method: 'DELETE' });
  },
}; 