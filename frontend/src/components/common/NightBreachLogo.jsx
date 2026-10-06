function NightBreachLogo({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <img
        src="/assets/nightbreach/branding/nightbreach_logo.png"
        alt="NightBreach"
        className={[
          'shrink-0 object-contain',
          compact ? 'h-9 w-9' : 'h-9 w-auto max-w-[170px]',
        ].join(' ')}
      />

      {!compact && (
        <div className="sr-only">
          <span>NightBreach</span>
        </div>
      )}
    </div>
  )
}

export default NightBreachLogo
