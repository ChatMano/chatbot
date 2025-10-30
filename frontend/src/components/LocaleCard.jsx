function LocaleCard({ locale, onEdit, onDelete, onTest, onRunNow }) {
  const getStatusBadge = () => {
    if (!locale.attivo) {
      return <span className="badge badge-danger">Disattivo</span>
    }

    if (locale.ultimo_log) {
      return locale.ultimo_log.successo ?
        <span className="badge badge-success">Ultimo: OK</span> :
        <span className="badge badge-danger">Ultimo: Errore</span>
    }

    return <span className="badge badge-warning">Mai eseguito</span>
  }

  return (
    <div className="locale-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <h3>{locale.nome}</h3>
        {getStatusBadge()}
      </div>

      <div className="locale-info">
        <p>
          <strong>Username:</strong>
          {locale.username}
        </p>
        <p>
          <strong>Orario:</strong>
          {locale.orario_esecuzione}
        </p>
        <p>
          <strong>Sheet ID:</strong>
          {locale.google_sheet_id.substring(0, 20)}...
        </p>
        {locale.ultimo_log && (
          <p>
            <strong>Ultimo run:</strong>
            {new Date(locale.ultimo_log.eseguito_at).toLocaleString('it-IT')}
          </p>
        )}
      </div>

      <div className="locale-actions">
        <button className="btn btn-primary" onClick={onRunNow} title="Esegui immediatamente questo locale">
          🚀 Esegui Ora
        </button>
        <button className="btn btn-success" onClick={onTest} title="Esegui test download">
          ▶️ Test
        </button>
        <button className="btn btn-secondary" onClick={onEdit}>
          ✏️ Modifica
        </button>
        <button className="btn btn-danger" onClick={onDelete}>
          🗑️ Elimina
        </button>
      </div>
    </div>
  )
}

export default LocaleCard
