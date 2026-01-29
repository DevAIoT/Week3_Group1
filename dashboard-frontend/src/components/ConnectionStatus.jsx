import { Badge } from '@/components/ui/badge'
import { Wifi, WifiOff } from 'lucide-react'

export function ConnectionStatus({ isConnected }) {
  return (
    <Badge
      variant="outline"
      className={
        isConnected
          ? 'bg-green-500/15 text-green-600 border-green-500/20 dark:text-green-400'
          : 'bg-yellow-500/15 text-yellow-600 border-yellow-500/20 dark:text-yellow-400'
      }
    >
      <span className="flex items-center gap-1.5">
        {isConnected ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
        {isConnected ? 'Live' : 'Polling'}
      </span>
    </Badge>
  )
}
