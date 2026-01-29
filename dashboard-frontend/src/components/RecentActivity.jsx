import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Clock } from 'lucide-react'
import { formatTimeAgo } from '../utils/dateHelpers'

const STAR_COLORS = {
  1: 'text-red-500',
  2: 'text-orange-500',
  3: 'text-yellow-500',
  4: 'text-lime-500',
  5: 'text-green-500',
}

export function RecentActivity({ ratings }) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-muted-foreground" />
          Recent Activity
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          {ratings.length === 0 ? (
            <div className="px-6 py-12 text-center text-muted-foreground">
              No ratings yet
            </div>
          ) : (
            ratings.slice(0, 20).map((rating, idx) => (
              <div key={rating.id}>
                {idx > 0 && <Separator />}
                <div className="px-6 py-3 flex items-center justify-between hover:bg-accent/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <span className={`text-2xl font-bold ${STAR_COLORS[rating.rating] || ''}`}>
                      {rating.rating}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">
                          {'★'.repeat(rating.rating)}{'☆'.repeat(5 - rating.rating)}
                        </span>
                        <Badge variant={rating.source === 'gesture' ? 'default' : 'secondary'} className="text-[10px]">
                          {rating.source}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatTimeAgo(rating.timestamp)}
                  </span>
                </div>
              </div>
            ))
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
