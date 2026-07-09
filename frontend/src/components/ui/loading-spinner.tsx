import React from 'react';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  text?: string;
}

const sizeStyles = {
  sm: 'h-5 w-5',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
};

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 'md', className, text }) => {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <div className="relative">
        <motion.div
          className={cn(
            'rounded-full border-2 border-[hsl(var(--muted))]',
            sizeStyles[size]
          )}
        />
        <motion.div
          className={cn(
            'absolute inset-0 rounded-full border-2 border-transparent border-t-[hsl(var(--primary))]',
            sizeStyles[size]
          )}
          animate={{ rotate: 360 }}
          transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
        />
        <motion.div
          className={cn(
            'absolute inset-[3px] rounded-full border-2 border-transparent border-t-indigo-400/50',
            size === 'sm' ? 'inset-[2px]' : size === 'lg' ? 'inset-[4px]' : 'inset-[3px]'
          )}
          animate={{ rotate: -360 }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
        />
      </div>
      {text && (
        <motion.p
          className="text-sm text-[hsl(var(--muted-foreground))]"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          {text}
        </motion.p>
      )}
    </div>
  );
};

export { LoadingSpinner };
export type { LoadingSpinnerProps };
