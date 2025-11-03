import React, { forwardRef } from 'react'

export interface LoaderProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Visible label next to/below the spinner (screen readers will read this) */
  label?: string
  /** Render inline (e.g., inside a button or sentence) */
  inline?: boolean
  /** Diameter of the spinner in px (affects border width proportionally) */
  size?: number
  /** Hide the visible label but keep it for screen readers */
  srOnly?: boolean
}

/**
 * Loader – accessible spinner using the `.loader` class from /public/styles.css
 * - Adds role="status" & aria-live="polite" so ATs announce progress
 * - Supports inline/block layouts and variable sizes
 */
const Loader = forwardRef<HTMLDivElement, LoaderProps>(function Loader(
  { label = 'Loading…', inline = false, size = 24, srOnly = false, className, style, ...rest },
  ref
) {
  const border = Math.max(2, Math.round(size / 6))
  const spinner = (
    <div
      className="loader"
      aria-hidden="true"
      style={{ width: size, height: size, borderWidth: border, ...(inline ? { marginRight: 8 } : { marginBottom: 8 }) }}
    />
  )

  const visuallyHidden: React.CSSProperties = {
    position: 'absolute',
    width: 1,
    height: 1,
    padding: 0,
    margin: -1,
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap',
    border: 0,
  }

  const Wrapper: React.ElementType = inline ? 'span' : 'div'

  return (
    <Wrapper
      ref={ref as any}
      role="status"
      aria-live="polite"
      className={className}
      style={{ display: inline ? 'inline-flex' : 'flex', alignItems: 'center', flexDirection: inline ? 'row' : 'column', ...style }}
      {...rest}
    >
      {spinner}
      {srOnly ? <span style={visuallyHidden}>{label}</span> : <span>{label}</span>}
    </Wrapper>
  )
})

export default Loader
