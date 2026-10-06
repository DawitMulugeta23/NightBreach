import nightbreachAssets from '../../config/nightbreachAssets'

const PATH_ICON_MAP = {
  cybersecurity_fundamentals: nightbreachAssets.icons.cyberSecurity,
  linux_fundamentals:          nightbreachAssets.icons.linux,
  windows_fundamentals:       nightbreachAssets.icons.windows,
  networking_fundamentals:    nightbreachAssets.icons.networking,
  defensive_security:         nightbreachAssets.icons.defensiveSecurity,
  offensive_security:         nightbreachAssets.icons.offensiveSecurity,
}

/**
 * Renders a NightBreach learning-path icon from the centralized asset map.
 *
 * Accepts either:
 *   - a stable path key (e.g. "linux_fundamentals")
 *   - a raw asset path (e.g. "/assets/nightbreach/icons/linux.png")
 *
 * The component intentionally preserves the previous sizing API:
 *   <PathIcon iconKey="linux_fundamentals" className="h-10 w-10" />
 */
function PathIcon({ iconKey, src, alt = '', className = '' }) {
  const resolvedSrc = src || PATH_ICON_MAP[iconKey]

  if (!resolvedSrc) {
    return null
  }

  return (
    <img
      src={resolvedSrc}
      alt={alt}
      loading="lazy"
      className={['shrink-0 object-contain', className].filter(Boolean).join(' ')}
    />
  )
}

export default PathIcon
export { PATH_ICON_MAP }
