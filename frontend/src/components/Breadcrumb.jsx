import React from 'react'
import { Link } from 'react-router-dom'

/**
 * items: [{ label, to? }] — last item is treated as current (not a link)
 */
function Breadcrumb({ items = [] }) {
  return (
    <div className="flex flex-wrap items-center gap-2 text-xs text-neutral-500 mb-6">
      {items.map((item, i) => {
        const isLast = i === items.length - 1
        return (
          <React.Fragment key={i}>
            {item.to && !isLast ? (
              <Link to={item.to} className="hover:text-emerald-400 transition-colors">
                {item.label}
              </Link>
            ) : (
              <span className={isLast ? 'text-neutral-900 dark:text-white' : 'text-emerald-400'}>{item.label}</span>
            )}
            {!isLast && <i className="fas fa-chevron-right text-[8px]"></i>}
          </React.Fragment>
        )
      })}
    </div>
  )
}

export default Breadcrumb
