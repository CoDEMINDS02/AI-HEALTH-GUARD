import { useLang } from '../context/LanguageContext.jsx'

export default function DisclaimerBanner() {
  const { t } = useLang()

  return (
    <div className="disclaimer-banner" role="note">
      {t('disclaimerBanner')}
    </div>
  )
}