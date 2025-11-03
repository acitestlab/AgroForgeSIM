import React, { forwardRef } from 'react'

type Variant = 'primary' | 'secondary' | 'ghost'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style; maps to classes defined in src/styles.css */
  variant?: Variant
  /** When true, shows a spinner and disables the button */
  loading?: boolean
  /** Stretch to container width */
  fullWidth?: boolean
  /** Optional icon slots */
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

/**
 * Reusable Button for AgroForgeSIM
 * - Variants align with .btn, .btn.secondary, .btn.ghost in styles.css
 * - Safe default type="button" to avoid accidental form submits
 * - Loading state with accessible aria-busy and spinner
 */
const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = 'primary',
    loading = false,
    fullWidth = false,
    leftIcon,
    rightIcon,
    className,
    type, // allow override, but default to "button"
    disabled,
    children,
    style,
    ...rest
  },
  ref
) {
  // Base + variant classes (maps to your styles.css)
  const base = 'btn'
  const variantClass =
    variant === 'secondary' ? 'secondary' : variant === 'ghost' ? 'ghost' : ''

  const classes = [base, variantClass, className].filter(Boolean).join(' ')
  const isDisabled = disabled || loading
  const mergedStyle = fullWidth ? { width: '100%', ...style } : style

  return (
    <button
      ref={ref}
      type={type ?? 'button'}
      className={classes}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      aria-live={loading ? 'polite' : undefined}
      style={mergedStyle}
      {...rest}
    >
      {leftIcon ? <span style={{ display: 'inline-flex', marginRight: 6 }}>{leftIcon}</span> : null}
      {children}
      {loading ? (
        <span
          className="loader"
          aria-hidden="true"
          style={{ marginLeft: 8, verticalAlign: -2, display: 'inline-block' }}
        />
      ) : null}
      {rightIcon ? <span style={{ display: 'inline-flex', marginLeft: 6 }}>{rightIcon}</span> : null}
    </button>
  )
})

export default Button
