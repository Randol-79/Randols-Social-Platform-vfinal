'use client';

import { useState, useEffect, createContext, useContext } from 'react';

// ============================================
// Toast Notification System
// ============================================

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info', duration = 5000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    
    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, duration);
    }
    
    return id;
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

function ToastContainer({ toasts, onDismiss }) {
  if (toasts.length === 0) return null;

  const typeStyles = {
    success: 'bg-marsh text-white',
    error: 'bg-cajun-red text-white',
    warning: 'bg-gold text-night',
    info: 'bg-bayou text-white'
  };

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-slide-up ${typeStyles[toast.type]}`}
        >
          <span className="text-lg">{icons[toast.type]}</span>
          <span className="text-sm font-medium">{toast.message}</span>
          <button
            onClick={() => onDismiss(toast.id)}
            className="ml-2 opacity-70 hover:opacity-100"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}

// ============================================
// Modal Component
// ============================================

export function Modal({ isOpen, onClose, title, children, size = 'md', footer }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className={`relative bg-white dark:bg-night-light rounded-2xl shadow-xl w-full ${sizeClasses[size]} max-h-[90vh] overflow-hidden flex flex-col`}>
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between px-6 py-4 border-b border-cream-dark dark:border-night">
            <h3 className="text-xl font-display font-bold text-night dark:text-cream">
              {title}
            </h3>
            <button 
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-cream-dark dark:hover:bg-night transition-colors"
            >
              <svg className="w-5 h-5 text-night/60 dark:text-cream/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {children}
        </div>
        
        {/* Footer */}
        {footer && (
          <div className="px-6 py-4 border-t border-cream-dark dark:border-night bg-cream-warm dark:bg-night">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================
// Dropdown Menu
// ============================================

export function Dropdown({ trigger, items, align = 'right' }) {
  const [isOpen, setIsOpen] = useState(false);

  const alignClasses = {
    left: 'left-0',
    right: 'right-0'
  };

  return (
    <div className="relative">
      <div onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </div>
      
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className={`absolute z-50 mt-2 w-48 bg-white dark:bg-night-light rounded-lg shadow-lg border border-cream-dark dark:border-night py-1 ${alignClasses[align]}`}>
            {items.map((item, index) => (
              item.divider ? (
                <hr key={index} className="my-1 border-cream-dark dark:border-night" />
              ) : (
                <button
                  key={index}
                  onClick={() => {
                    item.onClick?.();
                    setIsOpen(false);
                  }}
                  disabled={item.disabled}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-cream-dark dark:hover:bg-night transition-colors ${
                    item.danger ? 'text-cajun-red' : 'text-night dark:text-cream'
                  } ${item.disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {item.icon && <span className="mr-2">{item.icon}</span>}
                  {item.label}
                </button>
              )
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ============================================
// Tabs Component
// ============================================

export function Tabs({ tabs, activeTab, onChange, variant = 'default' }) {
  const variants = {
    default: {
      container: 'border-b border-cream-dark dark:border-night',
      tab: 'px-4 py-3 text-sm font-medium transition-colors',
      active: 'text-cajun-red border-b-2 border-cajun-red -mb-px',
      inactive: 'text-night/60 dark:text-cream/60 hover:text-night dark:hover:text-cream'
    },
    pills: {
      container: 'bg-cream-dark dark:bg-night rounded-lg p-1 inline-flex',
      tab: 'px-4 py-2 text-sm font-medium rounded-md transition-all',
      active: 'bg-white dark:bg-night-light text-night dark:text-cream shadow',
      inactive: 'text-night/60 dark:text-cream/60 hover:text-night dark:hover:text-cream'
    }
  };

  const style = variants[variant];

  return (
    <div className={style.container}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`${style.tab} ${activeTab === tab.id ? style.active : style.inactive}`}
        >
          {tab.icon && <span className="mr-2">{tab.icon}</span>}
          {tab.label}
          {tab.count !== undefined && (
            <span className="ml-2 px-2 py-0.5 bg-cajun-red/10 text-cajun-red text-xs rounded-full">
              {tab.count}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}

// ============================================
// Loading Spinner
// ============================================

export function Spinner({ size = 'md', className = '' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className={`${sizeClasses[size]} ${className}`}>
      <svg className="animate-spin" viewBox="0 0 24 24" fill="none">
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    </div>
  );
}

// ============================================
// Badge Component
// ============================================

export function Badge({ children, variant = 'default', size = 'md' }) {
  const variants = {
    default: 'bg-cream-dark dark:bg-night text-night dark:text-cream',
    primary: 'bg-cajun-red text-white',
    secondary: 'bg-rust text-white',
    success: 'bg-marsh text-white',
    warning: 'bg-gold text-night',
    danger: 'bg-cajun-red text-white',
    info: 'bg-bayou text-white',
    outline: 'border border-current bg-transparent'
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm'
  };

  return (
    <span className={`inline-flex items-center font-medium rounded-full ${variants[variant]} ${sizes[size]}`}>
      {children}
    </span>
  );
}

// ============================================
// Progress Bar
// ============================================

export function ProgressBar({ value, max = 100, color = 'primary', showLabel = false, size = 'md' }) {
  const percentage = Math.min((value / max) * 100, 100);

  const colors = {
    primary: 'bg-cajun-gradient',
    success: 'bg-marsh',
    warning: 'bg-gold',
    danger: 'bg-cajun-red',
    info: 'bg-bayou'
  };

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between text-xs mb-1">
          <span className="text-night/60 dark:text-cream/60">Progress</span>
          <span className="font-medium text-night dark:text-cream">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={`w-full bg-cream-dark dark:bg-night rounded-full overflow-hidden ${sizes[size]}`}>
        <div
          className={`${colors[color]} ${sizes[size]} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// ============================================
// Avatar Component
// ============================================

export function Avatar({ src, alt, name, size = 'md', status }) {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg'
  };

  const statusColors = {
    online: 'bg-marsh',
    offline: 'bg-gray-400',
    busy: 'bg-cajun-red',
    away: 'bg-gold'
  };

  const initials = name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <div className="relative inline-block">
      {src ? (
        <img
          src={src}
          alt={alt || name}
          className={`${sizeClasses[size]} rounded-full object-cover`}
        />
      ) : (
        <div className={`${sizeClasses[size]} rounded-full bg-cajun-gradient flex items-center justify-center text-white font-medium`}>
          {initials}
        </div>
      )}
      {status && (
        <span className={`absolute bottom-0 right-0 w-3 h-3 ${statusColors[status]} border-2 border-white dark:border-night-light rounded-full`} />
      )}
    </div>
  );
}

// ============================================
// Card Component
// ============================================

export function Card({ children, className = '', hover = false, onClick }) {
  return (
    <div 
      onClick={onClick}
      className={`
        bg-white dark:bg-night-light rounded-xl p-6 shadow-sm border border-cream-dark dark:border-night
        ${hover ? 'hover:shadow-lg transition-shadow cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

// ============================================
// Empty State Component
// ============================================

export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="text-center py-12">
      {icon && <div className="text-5xl mb-4">{icon}</div>}
      <h3 className="text-lg font-semibold text-night dark:text-cream mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-night/60 dark:text-cream/60 mb-4 max-w-md mx-auto">
          {description}
        </p>
      )}
      {action}
    </div>
  );
}

// ============================================
// Stat Card Component
// ============================================

export function StatCard({ icon, label, value, trend, trendValue, description }) {
  const trendColors = {
    up: 'text-marsh',
    down: 'text-cajun-red',
    neutral: 'text-night/60 dark:text-cream/60'
  };

  const trendIcons = {
    up: '↑',
    down: '↓',
    neutral: '→'
  };

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div className="w-12 h-12 rounded-xl bg-cajun-gradient flex items-center justify-center text-white text-xl">
          {icon}
        </div>
        {trend && (
          <span className={`flex items-center gap-1 text-sm font-medium ${trendColors[trend]}`}>
            {trendIcons[trend]} {trendValue}
          </span>
        )}
      </div>
      <div className="mt-4">
        <p className="text-sm text-night/60 dark:text-cream/60">{label}</p>
        <p className="text-2xl font-bold text-night dark:text-cream mt-1">{value}</p>
        {description && (
          <p className="text-xs text-night/50 dark:text-cream/50 mt-1">{description}</p>
        )}
      </div>
    </Card>
  );
}

// ============================================
// Toggle Switch
// ============================================

export function Toggle({ checked, onChange, label, disabled = false }) {
  return (
    <label className={`flex items-center gap-3 ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}>
      <div className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only"
        />
        <div className={`w-11 h-6 rounded-full transition-colors ${checked ? 'bg-cajun-red' : 'bg-cream-dark dark:bg-night'}`}>
          <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${checked ? 'translate-x-5' : ''}`} />
        </div>
      </div>
      {label && (
        <span className="text-sm text-night dark:text-cream">{label}</span>
      )}
    </label>
  );
}

// ============================================
// Search Input
// ============================================

export function SearchInput({ value, onChange, placeholder = 'Search...', className = '' }) {
  return (
    <div className={`relative ${className}`}>
      <svg
        className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-night/40 dark:text-cream/40"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream placeholder-night/40 dark:placeholder-cream/40 focus:ring-2 focus:ring-cajun-red focus:border-transparent"
      />
    </div>
  );
}

// ============================================
// Skeleton Loader
// ============================================

export function Skeleton({ className = '', variant = 'text' }) {
  const variants = {
    text: 'h-4 rounded',
    circle: 'rounded-full',
    rect: 'rounded-lg'
  };

  return (
    <div className={`bg-cream-dark dark:bg-night animate-pulse ${variants[variant]} ${className}`} />
  );
}

// ============================================
// Alert Component
// ============================================

export function Alert({ type = 'info', title, children, onDismiss }) {
  const types = {
    info: {
      bg: 'bg-bayou/10 border-bayou/20',
      icon: 'ℹ️',
      text: 'text-bayou'
    },
    success: {
      bg: 'bg-marsh/10 border-marsh/20',
      icon: '✓',
      text: 'text-marsh'
    },
    warning: {
      bg: 'bg-gold/10 border-gold/20',
      icon: '⚠️',
      text: 'text-gold'
    },
    error: {
      bg: 'bg-cajun-red/10 border-cajun-red/20',
      icon: '✕',
      text: 'text-cajun-red'
    }
  };

  const style = types[type];

  return (
    <div className={`flex items-start gap-3 p-4 rounded-lg border ${style.bg}`}>
      <span className={`text-lg ${style.text}`}>{style.icon}</span>
      <div className="flex-1">
        {title && (
          <h4 className={`font-medium ${style.text} mb-1`}>{title}</h4>
        )}
        <div className="text-sm text-night/70 dark:text-cream/70">
          {children}
        </div>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="text-night/40 hover:text-night dark:text-cream/40 dark:hover:text-cream">
          ✕
        </button>
      )}
    </div>
  );
}

// ============================================
// Date Picker Helper
// ============================================

export function DatePicker({ value, onChange, label, min, max }) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-night dark:text-cream mb-2">
          {label}
        </label>
      )}
      <input
        type="datetime-local"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        min={min}
        max={max}
        className="w-full px-4 py-2.5 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream focus:ring-2 focus:ring-cajun-red focus:border-transparent"
      />
    </div>
  );
}

// ============================================
// Select Component
// ============================================

export function Select({ value, onChange, options, label, placeholder = 'Select...' }) {
  return (
    <div>
      {label && (
        <label className="block text-sm font-medium text-night dark:text-cream mb-2">
          {label}
        </label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2.5 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream focus:ring-2 focus:ring-cajun-red focus:border-transparent appearance-none"
      >
        <option value="">{placeholder}</option>
        {options.map(option => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
