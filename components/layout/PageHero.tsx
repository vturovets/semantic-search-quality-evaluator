import { ReactNode } from 'react'

interface PageHeroProps {
  title: string;
  subtitle?: string;
  badges?: BadgeItem[];
  children?: ReactNode;
  className?: string;
}

interface BadgeItem {
  label: string;
  variant?: 'blue' | 'green' | 'purple' | 'gray';
}

export function PageHero({ 
  title, 
  subtitle, 
  badges = [], 
  children, 
  className = '' 
}: PageHeroProps) {
  const getBadgeClasses = (variant: BadgeItem['variant'] = 'blue') => {
    const variants = {
      blue: 'bg-blue-100 text-blue-800',
      green: 'bg-green-100 text-green-800',
      purple: 'bg-purple-100 text-purple-800',
      gray: 'bg-gray-100 text-gray-800'
    }
    return variants[variant]
  }

  return (
    <div className={`mb-6 sm:mb-8 ${className}`}>
      <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-3 sm:mb-4">
        {title}
      </h2>
      
      {subtitle && (
        <p className="text-base sm:text-lg text-gray-600 mb-4 sm:mb-6">
          {subtitle}
        </p>
      )}
      
      {badges.length > 0 && (
        <div className="flex flex-wrap gap-2 sm:gap-3 mb-4 sm:mb-6">
          {badges.map((badge, index) => (
            <span
              key={index}
              className={`inline-flex items-center px-2.5 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${getBadgeClasses(badge.variant)}`}
            >
              {badge.label}
            </span>
          ))}
        </div>
      )}
      
      {children}
    </div>
  )
}