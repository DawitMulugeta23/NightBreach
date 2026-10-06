function SectionHeader({ title, description, action }) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div>
        <h2 className="nb-section-title">{title}</h2>
        {description && (
          <p className="mt-1 text-xs text-slate-500">{description}</p>
        )}
      </div>

      {action}
    </div>
  )
}

export default SectionHeader
