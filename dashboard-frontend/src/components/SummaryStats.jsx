import { Card, CardContent } from '@/components/ui/card'
import { BarChart3, Star, TrendingUp, TrendingDown } from 'lucide-react'

const STATS_CONFIG = [
  { key: 'count', label: 'Total Ratings', icon: BarChart3, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  { key: 'average', label: 'Average', icon: Star, color: 'text-amber-500', bg: 'bg-amber-500/10', format: v => v?.toFixed(2) || 'N/A' },
  { key: 'max', label: 'Highest', icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-500/10' },
  { key: 'min', label: 'Lowest', icon: TrendingDown, color: 'text-red-500', bg: 'bg-red-500/10' },
]

export function SummaryStats({ summary }) {
  if (!summary) return null

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 [&>*]:min-w-0">
      {STATS_CONFIG.map(({ key, label, icon: Icon, color, bg, format }) => (
        <Card key={key} className="transition-shadow hover:shadow-md">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">{label}</p>
                <p className="text-3xl font-bold mt-1">
                  {format ? format(summary[key]) : (summary[key] ?? 'N/A')}
                </p>
              </div>
              <div className={`${bg} ${color} p-3 rounded-lg`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
