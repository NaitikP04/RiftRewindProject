/**
 * Core type definitions for RiftReview player data
 */

export interface Champion {
  name: string
  winRate: number
  games: number
}

export interface Highlight {
  stat: string
  value: string
}

export interface Progress {
  season: string[]
  [key: string]: number[] | string[]
}

export interface RankEvent {
  message: string
  champion: string
  effect: "win" | "loss" | "streak"
}

export interface PlayerData {
  username: string
  tag: string
  displayName: string
  profilePicture: string
  mainRole: string
  topChampions: Champion[]
  highlights: Highlight[]
  aiInsight: string
  progress: Progress
  personality: string
  seasonMonths: string[]
  rankTimeline: string[]
  rankEvents: Record<string, RankEvent>
}

export type DemoKey = "demo1" | "demo2" | "demo3"

export interface MockDataSet {
  [key: string]: PlayerData
}
