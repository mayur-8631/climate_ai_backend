import React, { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'glow-emerald' | 'glow-cyan' | 'elevated';
  onClick?: () => void;
}

export function Card({
  children,
  className = '',
  variant = 'default',
  onClick,
}: CardProps) {
  let variantClasses =
    'bg-[#0C2033]/90 border border-[#1A3954] shadow-lg shadow-black/20';

  if (variant === 'glow-emerald') {
    variantClasses =
      'bg-gradient-to-b from-[#0F2942] to-[#091D30] border border-emerald-500/30 shadow-[0_0_25px_rgba(16,185,129,0.12)]';
  } else if (variant === 'glow-cyan') {
    variantClasses =
      'bg-gradient-to-b from-[#0F2942] to-[#091D30] border border-cyan-500/30 shadow-[0_0_25px_rgba(34,211,238,0.12)]';
  } else if (variant === 'elevated') {
    variantClasses =
      'bg-[#10273D] border border-[#224A6D] shadow-xl shadow-black/40';
  }

  return (
    <div
      onClick={onClick}
      className={`rounded-xl backdrop-blur-md transition-all duration-200 ${variantClasses} ${
        onClick ? 'cursor-pointer hover:border-cyan-400/40 hover:-translate-y-0.5' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
}

export function CardHeader({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`px-5 py-4 border-b border-[#1A3954]/70 flex items-center justify-between ${className}`}
    >
      {children}
    </div>
  );
}

export function CardTitle({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <h3
      className={`text-base font-semibold text-slate-100 flex items-center gap-2 ${className}`}
    >
      {children}
    </h3>
  );
}

export function CardDescription({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <p className={`text-xs text-slate-400 mt-0.5 ${className}`}>{children}</p>
  );
}

export function CardContent({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={`p-5 ${className}`}>{children}</div>;
}

export function CardFooter({
  children,
  className = '',
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`px-5 py-3.5 border-t border-[#1A3954]/60 bg-[#071827]/40 rounded-b-xl flex items-center justify-between text-xs text-slate-400 ${className}`}
    >
      {children}
    </div>
  );
}

