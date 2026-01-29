import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { ChartContainer } from '@/components/ui/chart'
import { RadialBarChart, RadialBar } from 'recharts'

const SATISFACTION_COLORS = {
  excellent: 'var(--color-chart-2)',
  good: 'var(--color-chart-4)',
  average: 'var(--color-chart-1)',
  poor: 'var(--color-chart-5)',
}

function getColor(avg) {
  if (avg >= 4) return SATISFACTION_COLORS.excellent
  if (avg >= 3) return SATISFACTION_COLORS.good
  if (avg >= 2) return SATISFACTION_COLORS.average
  return SATISFACTION_COLORS.poor
}

function getLabel(avg) {
  if (avg >= 4.5) return 'Excellent'
  if (avg >= 3.5) return 'Good'
  if (avg >= 2.5) return 'Average'
  if (avg >= 1.5) return 'Poor'
  return 'Very Poor'
}

const chartConfig = {
  score: { label: 'Satisfaction' },
}

export function SatisfactionGauge({ average }) {
  const value = average || 0
  const percentage = (value / 5) * 100
  const color = getColor(value)

  const data = [
    { name: 'score', value: percentage, fill: color },
  ]

  return (
    <Card>
      <CardHeader className="pb-0">
        <CardTitle className="text-base">Satisfaction</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        {value === 0 ? (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            No data
          </div>
        ) : (
          <div className="relative w-full h-[180px]">
            <ChartContainer config={chartConfig} className="aspect-auto h-[180px] w-full">
              <RadialBarChart
                cx="50%"
                cy="50%"
                innerRadius="60%"
                outerRadius="85%"
                barSize={14}
                data={data}
                startAngle={180}
                endAngle={0}
              >
                <RadialBar
                  background
                  dataKey="value"
                  cornerRadius={10}
                />
              </RadialBarChart>
            </ChartContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center mt-4">
              <span className="text-3xl font-bold" style={{ color }}>{value.toFixed(1)}</span>
              <span className="text-sm text-muted-foreground">{getLabel(value)}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
