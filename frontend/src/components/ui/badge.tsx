import React from 'react';
import { cn } from '@/lib/utils';

type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantStyles: Record<BadgeVariant, string> = {
  default:
    'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] shadow-sm',
  secondary:
    'bg-[hsl(var(--secondary))] text-[hsl(var(--secondary-foreground))]',
  destructive:
    'bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))] shadow-sm',
  outline:
    'border border-[hsl(var(--border))] text-[hsl(var(--foreground))]',
  success:
    'bg-emerald-500/15 text-emerald-500 border border-emerald-500/20',
  warning:
    'bg-amber-500/15 text-amber-500 border border-amber-500/20',
};

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
        variantStyles[variant],
        className
      )}
      {...props}
    />
  )
);

Badge.displayName = 'Badge';

export { Badge };
export type { BadgeProps, BadgeVariant };
