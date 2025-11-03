import React, { forwardRef, PropsWithChildren, ReactNode } from 'react'

export interface CardProps extends PropsWithChildren {
  /** Optional heading displayed at the top of the card */
  title?: ReactNode
  /** Optional subheading rendered next to/below the title */
  subtitle?: ReactNode
  /** Optional footer area rendered at the bottom of the card */
  footer?: ReactNode
  /** Additional classes merged with the base `card` style (from /public/styles.css) */
  className?: string
  /** Semantic element to render */
  as?: 'div' | 'section' | 'article'
  /** Optional role; e.g., role="region" for landmark navigation */
  role?: React.AriaRole
  /** Optional id for the card container */
  id?: string
}

/**
 * Card – lightweight container aligned with `.card` styles in styles.css.
 * - Offers title/subtitle/footer slots
 * - Accessible by default (aria-labelledby when title is provided)
 * - Allows semantic element selection via `as`
 */
const Card = forwardRef<HTMLElement, CardProps>(function Card(
  { title, subtitle, footer, className, as = 'section', id, role, children },
  ref
) {
  const Component = as as any
  const headingId = id ? `${id}__title` : undefined
  const hasHeader = Boolean(title || subtitle)
  const classes = ['card', className].filter(Boolean).join(' ')

  return (
    <Component
      id={id}
      className={classes}
      role={role}
      aria-labelledby={hasHeader && headingId ? headingId : undefined}
      ref={ref as any}
    >
      {hasHeader && (
        <div style={{ marginBottom: 8 }}>
          {title && (
            <h3 id={headingId} style={{ margin: 0 }}>
              {title}
            </h3>
          )}
          {subtitle && (
            <div style={{ opacity: 0.8, marginTop: title ? 4 : 0 }}>{subtitle}</div>
          )}
        </div>
      )}

      <div>{children}</div>

      {footer && (
        <div style={{ marginTop: 10, opacity: 0.85 }}>
          {footer}
        </div>
      )}
    </Component>
  )
})

export default Card
