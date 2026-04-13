// Common type definitions

export interface NavigationItem {
  label: string;
  href: string;
  isActive?: boolean;
}

export interface DemoConfig {
  productName: string;
  tagline: string;
  navigation: NavigationItem[];
}

export interface UIConstants {
  maxContentWidth: string;
  breakpoints: {
    mobile: string;
    tablet: string;
    desktop: string;
  };
  colors: {
    primary: string;
    success: string;
    warning: string;
    danger: string;
  };
  spacing: {
    section: string;
    card: string;
    element: string;
  };
}

// Component prop types
export interface StatusBadgeProps {
  status: 'COMPLETED' | 'RUNNING' | 'FAILED' | 'PENDING';
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export interface KPIStatCardProps {
  title: string;
  value: string;
  unit?: string;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    percentage: number;
    label?: string;
  };
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export interface ActionButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export interface SideDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  position?: 'left' | 'right';
  size?: 'sm' | 'md' | 'lg';
}

export interface TooltipInfoProps {
  content: string | React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  trigger?: 'hover' | 'click' | 'focus';
  maxWidth?: string;
}

export interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon?: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export interface ProgressBarProps {
  label: string;
  value: string;
  percentage: number;
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

export interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}
