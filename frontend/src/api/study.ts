import api from './axios'

export interface StudyCard { card_id: number; front: string; back: string }
export interface NextCardResponse { card?: StudyCard | null; message?: string; card_id?: number; front?: string; back?: string }
export interface Progress { total_cards: number; due_cards: number; new_cards: number; completed_cards: number }
export type StudyQuality = 0 | 1 | 2 | 3 | 4 | 5

export const startSession = async (deckId: number) => api.post(`/study/start/${deckId}`)
export const getNextCard = async (deckId: number) => (await api.get<NextCardResponse>(`/study/next-card/${deckId}`)).data
export const submitAnswer = async (cardId: number, quality: StudyQuality) =>
  api.post('/study/submit-answer', null, { params: { card_id: cardId, quality } })
export const getProgress = async (deckId: number) => (await api.get<Progress>(`/study/progress/${deckId}`)).data
export async function getPracticeCards(deckId: number) {
  const response = await api.get(`/study/practice/${deckId}`)
  return response.data
}