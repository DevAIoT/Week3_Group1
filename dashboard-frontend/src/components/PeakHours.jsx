import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'

const chartConfig = {
  count: { label: 'Ratings', color: 'var(--color-chart-4)' },
}

export function PeakHours({ ratings }) {
  const hourCounts = new Array(24).fill(0)

  ratings.forEach(r => {
    const hour = new Date(r.timestamp).getHours()
    hourCounts[hour]++
  })

  const data = hourCounts.map((count, hour) => ({
    hour: `${String(hour).padStart(2, '0')}:00`,
    count,
  }))

  const maxCount = Math.max(...hourCounts)

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Peak Hours</CardTitle>
      </CardHeader>
      <CardContent>
        {maxCount === 0 ? (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            No data available
          </div>
        ) : (
          <ChartContainer config={chartConfig} className="aspect-auto h-[200px] w-full">
            <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-border" />
              <XAxis dataKey="hour" tick={{ fontSize: 10 }} interval={2} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar
                dataKey="count"
                fill="var(--color-count)"
                radius={[2, 2, 0, 0]}
              />
            </BarChart>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
