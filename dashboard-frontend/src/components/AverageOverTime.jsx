import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart'
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts'

const PERIODS = [
  { value: 'hour', label: '24h' },
  { value: 'day', label: '7d' },
  { value: 'week', label: '4w' },
]

const chartConfig = {
  average: { label: 'Average', color: 'var(--color-chart-1)' },
}

function formatLabel(timestamp, period) {
  const d = new Date(timestamp)
  if (period === 'hour') return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

export function AverageOverTime({ data, period, onPeriodChange }) {
  const [activePeriod, setActivePeriod] = useState(period || 'hour')

  const handlePeriodChange = (p) => {
    setActivePeriod(p)
    onPeriodChange?.(p)
  }

  const chartData = data.map(d => ({
    ...d,
    label: formatLabel(d.timestamp, activePeriod),
  }))

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Average Over Time</CardTitle>
          <Tabs value={activePeriod} onValueChange={handlePeriodChange}>
            <TabsList>
              {PERIODS.map(p => (
                <TabsTrigger key={p.value} value={p.value}>
                  {p.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            No data available
          </div>
        ) : (
          <ChartContainer config={chartConfig} className="aspect-auto h-[200px] w-full">
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-border" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 12 }} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="average"
                stroke="var(--color-average)"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
