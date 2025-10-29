import LocaleCard from './LocaleCard'

function LocaleList({ locali, onEdit, onDelete, onTest }) {
  if (locali.length === 0) {
    return (
      <div className="empty-state">
        <h3>Nessun locale configurato</h3>
        <p>Aggiungi il tuo primo locale per iniziare</p>
      </div>
    )
  }

  return (
    <div className="locali-grid">
      {locali.map((locale) => (
        <LocaleCard
          key={locale.id}
          locale={locale}
          onEdit={() => onEdit(locale)}
          onDelete={() => onDelete(locale.id)}
          onTest={() => onTest(locale.id)}
        />
      ))}
    </div>
  )
}

export default LocaleList
