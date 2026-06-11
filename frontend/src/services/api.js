import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 70000
})

export function generateTravel(data) {
  return http.post('/travel/generate', data)
}

export function listTravels() {
  return http.get('/travel/list')
}

export function getTravel(id) {
  return http.get(`/travel/${id}`)
}

export function getYearSummary() {
  return http.post('/travel/year-summary')
}

export function sendChatMessage(data) {
  return http.post('/chat/message', data)
}

export function generateTravelFromChat({ sessionId, travelInfo, images }) {
  const form = new FormData()
  form.append('session_id', sessionId)
  form.append('travel_info_json', JSON.stringify(travelInfo || {}))
  ;(images || []).forEach((file) => {
    form.append('images', file)
  })
  return http.post('/chat/generate-travel-log', form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function recommendNearby(data) {
  return http.post('/recommend/nearby', data)
}
