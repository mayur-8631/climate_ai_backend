import React, { ButtonHTMLAttributes, ReactNode } from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: ReactNode;
  className?: string;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  icon,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  let variantStyles =
    'bg-emerald-500 hover:bg-emerald-400 text-navy-950 font-semibold shadow-lg shadow-emerald-500/20 active:scale-[0.98]';

  if (variant === 'secondary') {
    variantStyles =
      'bg-[#13304A] hover:bg-[#1A4164] text-cyan-300 border border-cyan-500/30 active:scale-[0.98]';
  } else if (variant === 'outline') {
    variantStyles =
      'bg-transparent hover:bg-[#102638] text-slate-200 border border-[#1A3954] hover:border-cyan-400/50 active:scale-[0.98]';
  } else if (variant === 'ghost') {
    variantStyles =
      'bg-transparent hover:bg-[#102638]/70 text-slate-300 hover:text-white active:scale-[0.98]';
  } else if (variant === 'danger') {
    variantStyles =
      'bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 active:scale-[0.98]';
  }

  let sizeStyles = 'px-4 py-2 text-sm rounded-lg';
  if (size === 'sm') sizeStyles = 'px-3 py-1.5 text-xs rounded-md';
  if (size === 'lg') sizeStyles = 'px-6 py-3 text-base rounded-xl';

  return (
    <button
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center gap-2 transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none ${variantStyles} ${sizeStyles} ${className}`}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-current" />
      ) : (
        icon && <span className="shrink-0">{icon}</span>
      )}
      <span>{children}</span>
    </button>
  );
}

