'use client'

import { useState } from 'react'
import { usePathname } from 'next/navigation'
import { User, Menu, X } from 'lucide-react'
import { demoConfig } from '../../lib/constants/demo-config'
import { NavigationItem } from '../../lib/types/shared'

interface AppHeaderProps {
  className?: string;
}

export function AppHeader({ className = '' }: AppHeaderProps) {
  const pathname = usePathname()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const getNavigationItems = (): NavigationItem[] => {
    return demoConfig.navigation.map(item => ({
      ...item,
      isActive: pathname === item.href
    }))
  }

  const navigationItems = getNavigationItems()

  return (
    <header className={`sticky top-0 z-50 bg-white/80 backdrop-blur-sm border-b border-gray-200 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Product Branding */}
          <div className="flex items-center">
            <h1 className="text-lg sm:text-xl font-bold text-gray-900 truncate">
              {demoConfig.productName}
            </h1>
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigationItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className={`pb-4 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm ${
                  item.isActive
                    ? 'text-blue-600 font-medium border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:scale-105'
                }`}
                aria-current={item.isActive ? 'page' : undefined}
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Desktop Right Side Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <button 
              className="text-gray-500 hover:text-gray-700 text-sm font-medium transition-all duration-300 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-sm px-2 py-1"
              aria-label="View demo flow"
            >
              View Demo Flow
            </button>
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center transition-all duration-300 hover:bg-blue-200 hover:scale-110 cursor-pointer">
              <User className="w-4 h-4 text-blue-600" aria-hidden="true" />
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden items-center space-x-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-blue-600" aria-hidden="true" />
            </div>
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="md:hidden p-2 text-gray-500 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-expanded={isMobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              {isMobileMenuOpen ? (
                <X className="w-5 h-5" aria-hidden="true" />
              ) : (
                <Menu className="w-5 h-5" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-4 py-2 space-y-1">
            {navigationItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`block px-3 py-3 text-base font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md min-h-[44px] ${
                  item.isActive
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
                aria-current={item.isActive ? 'page' : undefined}
              >
                {item.label}
              </a>
            ))}
            <button 
              className="block w-full text-left px-3 py-3 text-base font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md min-h-[44px]"
              onClick={() => setIsMobileMenuOpen(false)}
              aria-label="View demo flow"
            >
              View Demo Flow
            </button>
          </div>
        </div>
      )}
    </header>
  )
}