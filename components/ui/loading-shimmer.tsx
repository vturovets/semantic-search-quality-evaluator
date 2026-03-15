export function LoadingShimmer() {
  return (
    <div className="animate-pulse space-y-3">
      <div className="h-4 bg-gray-200 rounded w-3/4 animate-shimmer"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2 animate-shimmer" style={{ animationDelay: '0.1s' }}></div>
    </div>
  )
}

export function ProductResultSkeleton() {
  return (
    <div className="p-3 sm:p-4 rounded-xl border border-gray-200 animate-fadeIn">
      <div className="flex flex-col sm:flex-row items-start gap-3 sm:gap-4">
        <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0 animate-pulse"></div>
        
        <div className="flex-1 min-w-0 w-full space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
            <div className="flex-1 space-y-2">
              <div className="h-5 bg-gray-200 rounded w-3/4 animate-shimmer"></div>
              <div className="h-4 bg-gray-200 rounded w-16 animate-shimmer" style={{ animationDelay: '0.1s' }}></div>
            </div>
            <div className="h-6 bg-gray-200 rounded w-20 animate-shimmer" style={{ animationDelay: '0.2s' }}></div>
          </div>
          
          <div className="h-4 bg-gray-200 rounded w-full animate-shimmer" style={{ animationDelay: '0.3s' }}></div>
          <div className="h-4 bg-gray-200 rounded w-5/6 animate-shimmer" style={{ animationDelay: '0.4s' }}></div>
          
          <div className="flex flex-wrap gap-1">
            <div className="h-6 bg-gray-200 rounded-full w-16 animate-shimmer" style={{ animationDelay: '0.5s' }}></div>
            <div className="h-6 bg-gray-200 rounded-full w-20 animate-shimmer" style={{ animationDelay: '0.6s' }}></div>
            <div className="h-6 bg-gray-200 rounded-full w-14 animate-shimmer" style={{ animationDelay: '0.7s' }}></div>
          </div>
        </div>
      </div>
    </div>
  )
}
