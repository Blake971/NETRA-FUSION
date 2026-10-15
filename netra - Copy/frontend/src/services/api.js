import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add response interceptor to handle non-JSON responses
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      const contentType = error.response.headers['content-type']
      if (contentType && !contentType.includes('application/json')) {
        // Backend returned non-JSON, convert to error
        return Promise.reject(new Error(error.response.data || 'Server returned non-JSON response'))
      }
    }
    return Promise.reject(error)
  }
)

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

export const startScan = async (domain) => {
  // Extract domain from URL if full URL is provided
  let cleanDomain = domain
  
  if (domain.startsWith('http://') || domain.startsWith('https://')) {
    try {
      const url = new URL(domain)
      cleanDomain = url.hostname
    } catch (e) {
      // If URL parsing fails, try basic extraction
      cleanDomain = domain.replace(/^https?:\/\//, '').split('/')[0]
    }
  }
  
  const response = await api.post('/scan', { domain: cleanDomain })
  return response.data
}

export const getScan = async (scanId) => {
  const response = await api.get(`/scan/${scanId}`)
  return response.data
}

export const getScanHistory = async () => {
  const response = await api.get('/scans')
  return response.data
}

export const getScanResults = async (scanId) => {
  const response = await api.get(`/scans/${scanId}`)
  return response.data
}

export const deleteScan = async (scanId) => {
  const response = await api.delete(`/scans/${scanId}`)
  return response.data
}

export const downloadReport = async (scanId) => {
  const response = await api.get(`/scans/${scanId}/report`, {
    responseType: 'blob'
  })
  return response
}

export const getGoogleDorks = async (domain) => {
  const response = await api.post(`/google-dork?domain=${encodeURIComponent(domain)}`)
  return response.data
}

export const getDigitalFootprint = async (domain) => {
  const response = await api.post(`/digital-footprint?domain=${encodeURIComponent(domain)}`)
  return response.data
}

export const getPersonDorks = async (personData) => {
  const response = await api.post('/person-dork', personData)
  return response.data
}

export default api
