import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor do obsługi błędów
api.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.detail || 'Wystąpił błąd serwera'
    return Promise.reject(new Error(message))
  }
)

export const analyzeText = (text) => api.post('/analyze', { text })
export const getResults  = (id)   => api.get(`/results/${id}`)
export const getHistory  = ()     => api.get('/history')
export const compareTexts = (text_a, text_b) => api.post('/compare', { text_a, text_b })
export const deleteAnalysis = (id) => api.delete(`/history/${id}`)

export default api
