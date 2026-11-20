import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import StudySession from './StudySession'
import {
  getNextCard,
  getProgress,
  startSession,
  submitAnswer,
} from '../api/study'

vi.mock('../api/study', () => ({
  getNextCard: vi.fn(),
  getProgress: vi.fn(),
  startSession: vi.fn(),
  submitAnswer: vi.fn(),
}))

const mockedStartSession = vi.mocked(startSession)
const mockedGetNextCard = vi.mocked(getNextCard)
const mockedGetProgress = vi.mocked(getProgress)
const mockedSubmitAnswer = vi.mocked(submitAnswer)

function renderSession() {
  return render(
    <MemoryRouter initialEntries={['/study/7']}>
      <Routes>
        <Route path="/study/:id" element={<StudySession />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('StudySession', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedStartSession.mockResolvedValue({} as never)
    mockedGetProgress.mockResolvedValue({
      total_cards: 1,
      due_cards: 0,
      new_cards: 1,
      completed_cards: 0,
    })
    mockedGetNextCard
      .mockResolvedValueOnce({ card_id: 42, front: 'Question', back: 'Answer' })
      .mockResolvedValueOnce({ card: null, message: 'No cards left to study.' })
    mockedSubmitAnswer.mockResolvedValue({} as never)
  })

  it('submits the Good SM-2 quality score after revealing the answer', async () => {
    const user = userEvent.setup()
    renderSession()

    await user.click(await screen.findByRole('button', { name: 'Reveal answer' }))

    expect(screen.getAllByText('Answer')).toHaveLength(2)
    expect(screen.getByRole('button', { name: 'Again' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Hard' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Good' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Easy' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Good' }))

    await waitFor(() => expect(mockedSubmitAnswer).toHaveBeenCalledWith(42, 4))
    expect(await screen.findByText('Session complete')).toBeInTheDocument()
  })
})
