import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  response => response,
  error => {
    const message = error.response?.data?.detail || 'Wystąpił błąd serwera'
    return Promise.reject(new Error(message))
  }
)

export const analyzeText   = (text)           => api.post('/analyze', { text })
export const getResults    = (id)             => api.get(`/results/${id}`)
export const getHistory    = ()               => api.get('/history')
export const compareTexts  = (text_a, text_b) => api.post('/compare', { text_a, text_b })
export const deleteAnalysis = (id)            => api.delete(`/history/${id}`)


export const downloadText = (id) => {
  const link = document.createElement('a')
  link.href = `/api/results/${id}/text`
  link.download = `tekst_analiza_${id}.txt`
  link.click()
}

export const exportReportJSON = (id) => {
  const link = document.createElement('a')
  link.href = `/api/results/${id}/export`
  link.download = `raport_analiza_${id}.json`
  link.click()
}

export const exportReportPDF = () => {
  window.print()
}

export default api