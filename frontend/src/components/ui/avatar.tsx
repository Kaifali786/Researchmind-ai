import React from 'react';
import { cn, getInitials } from '@/lib/utils';

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizeStyles = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-14 w-14 text-lg',
};

const Avatar: React.FC<AvatarProps> = ({ src, alt, name, size = 'md', className, ...props }) => {
  const [imgError, setImgError] = React.useState(false);

  const fallback = name ? getInitials(name) : '?';

  return (
    <div
      className={cn(
        'relative inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-indigo-500 to-blue-600 font-semibold text-white ring-2 ring-[hsl(var(--background))] transition-transform duration-200 hover:scale-105',
        sizeStyles[size],
        className
      )}
      {...props}
    >
      {src && !imgError ? (
        <img
          src={src}
          alt={alt || name || 'Avatar'}
          className="h-full w-full object-cover"
          onError={() => setImgError(true)}
        />
      ) : (
        <span className="select-none">{fallback}</span>
      )}
    </div>
  );
};

export { Avatar };
export type { AvatarProps };
