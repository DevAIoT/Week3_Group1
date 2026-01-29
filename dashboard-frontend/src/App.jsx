import { useRatings } from './hooks/useRatings'
import { DashboardHeader } from './components/DashboardHeader'
import { SummaryStats } from './components/SummaryStats'
import { SatisfactionGauge } from './components/SatisfactionGauge'
import { RatingDistribution } from './components/RatingDistribution'
import { PeakHours } from './components/PeakHours'
import { AverageOverTime } from './components/AverageOverTime'
import { ActivityVolume } from './components/ActivityVolume'
import { RecentActivity } from './components/RecentActivity'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

function SkeletonCard() {
  return (
    <Card>
      <CardContent className="p-6 space-y-3">
        <Skeleton className="h-4 w-1/3" />
        <Skeleton className="h-8 w-1/2" />
      </CardContent>
    </Card>
  )
}

function SkeletonChart() {
  return (
    <Card>
      <CardContent className="p-6 space-y-3">
        <Skeleton className="h-4 w-1/4" />
        <Skeleton className="h-[200px] w-full" />
      </CardContent>
    </Card>
  )
}

function App() {
  const {
    ratings, summary, timeline, timelinePeriod,
    distribution, loading,
    isConnected, refetch, fetchTimeline,
  } = useRatings()

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader isConnected={isConnected} onRefresh={refetch} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {loading ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 [&>*]:min-w-0">
              {[...Array(4)].map((_, i) => <SkeletonCard key={i} />)}
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 [&>*]:min-w-0">
              {[...Array(3)].map((_, i) => <SkeletonChart key={i} />)}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 [&>*]:min-w-0">
              {[...Array(2)].map((_, i) => <SkeletonChart key={i} />)}
            </div>
          </>
        ) : (
          <>
            <SummaryStats summary={summary} />

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 [&>*]:min-w-0">
              <SatisfactionGauge average={summary?.average} />
              <RatingDistribution distribution={distribution} />
              <PeakHours ratings={ratings} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 [&>*]:min-w-0">
              <AverageOverTime
                data={timeline}
                period={timelinePeriod}
                onPeriodChange={fetchTimeline}
              />
              <ActivityVolume data={timeline} />
            </div>

            <RecentActivity ratings={ratings} />
          </>
        )}
      </main>
    </div>
  )
}

export default App
