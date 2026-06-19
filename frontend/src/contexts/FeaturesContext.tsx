import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { getFeatures } from '../services/api'
import type { PremiumFeatures } from '../types'

const ALL_TRUE: PremiumFeatures = { notifications: true, body_tracking: true, store: true }

interface FeaturesContextValue { premium: PremiumFeatures }

const FeaturesContext = createContext<FeaturesContextValue | null>(null)

export function FeaturesProvider({ children }: { children: ReactNode }) {
  const [premium, setPremium] = useState<PremiumFeatures>(ALL_TRUE)

  useEffect(() => {
    getFeatures().then(data => { if (data) setPremium(data.premium) })
  }, [])

  return <FeaturesContext.Provider value={{ premium }}>{children}</FeaturesContext.Provider>
}

export function useFeatures(): FeaturesContextValue {
  const ctx = useContext(FeaturesContext)
  if (!ctx) throw new Error('useFeatures must be used inside FeaturesProvider')
  return ctx
}
