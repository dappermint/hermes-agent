import { beforeEach, describe, expect, it, type Mock, vi } from 'vitest'

import { $hapticsMuted } from '@/store/haptics'

import { type HapticTrigger, registerHapticTrigger, triggerHaptic } from './haptics'

describe('triggerHaptic rate limiting', () => {
  let trigger: Mock<HapticTrigger>

  beforeEach(() => {
    $hapticsMuted.set(false)
    trigger = vi.fn<HapticTrigger>(() => undefined)
    registerHapticTrigger(trigger)
  })

  it('never drops a gesture haptic, however fast the user toggles', () => {
    for (let i = 0; i < 20; i++) {
      triggerHaptic('tap')
    }

    expect(trigger).toHaveBeenCalledTimes(20)
  })

  it('still caps automatic haptics so a background storm cannot buzz the actuator', () => {
    for (let i = 0; i < 20; i++) {
      triggerHaptic('error')
    }

    expect(trigger.mock.calls.length).toBeLessThanOrEqual(5)
  })

  it('stays silent when muted', () => {
    $hapticsMuted.set(true)
    triggerHaptic('tap')
    expect(trigger).not.toHaveBeenCalled()
    $hapticsMuted.set(false)
  })
})
