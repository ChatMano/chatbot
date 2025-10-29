import { useState } from 'react'

function LocaleForm({ locale, onSubmit, onClose }) {
  const [formData, setFormData] = useState({
    nome: locale?.nome || '',
    username: locale?.username || '',
    password: '',
    orario_esecuzione: locale?.orario_esecuzione || '03:00',
    google_sheet_id: locale?.google_sheet_id || '',
    locale_selector: locale?.locale_selector || '',
    attivo: locale?.attivo !== undefined ? locale.attivo : true
  })

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    // Validazione base
    if (!formData.nome || !formData.username || !formData.google_sheet_id) {
      alert('Compila tutti i campi obbligatori')
      return
    }

    // Se è una modifica e la password è vuota, non inviarla
    const dataToSubmit = { ...formData }
    if (locale && !dataToSubmit.password) {
      delete dataToSubmit.password
    }

    onSubmit(dataToSubmit)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{locale ? 'Modifica Locale' : 'Nuovo Locale'}</h2>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="nome">
              Nome Locale *
            </label>
            <input
              type="text"
              id="nome"
              name="nome"
              value={formData.nome}
              onChange={handleChange}
              placeholder="Es: Roma Centro"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="username">
              Username *
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Es: 4gruppotessar@ipratico.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password {locale ? '(lascia vuoto per non modificare)' : '*'}
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required={!locale}
            />
          </div>

          <div className="form-group">
            <label htmlFor="orario_esecuzione">
              Orario Esecuzione *
            </label>
            <input
              type="time"
              id="orario_esecuzione"
              name="orario_esecuzione"
              value={formData.orario_esecuzione}
              onChange={handleChange}
              required
            />
            <small style={{ color: '#666', fontSize: '0.85rem' }}>
              Orario in cui verrà eseguito il download automatico
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="google_sheet_id">
              Google Sheet ID *
            </label>
            <input
              type="text"
              id="google_sheet_id"
              name="google_sheet_id"
              value={formData.google_sheet_id}
              onChange={handleChange}
              placeholder="Es: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
              required
            />
            <small style={{ color: '#666', fontSize: '0.85rem' }}>
              L'ID del foglio Google Sheets dove salvare i dati
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="locale_selector">
              Selettore Locale (opzionale)
            </label>
            <input
              type="text"
              id="locale_selector"
              name="locale_selector"
              value={formData.locale_selector}
              onChange={handleChange}
              placeholder="Es: #locale-roma o URL specifico"
            />
            <small style={{ color: '#666', fontSize: '0.85rem' }}>
              Selettore CSS o identificatore per selezionare questo locale su iPratico
            </small>
          </div>

          <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <input
              type="checkbox"
              id="attivo"
              name="attivo"
              checked={formData.attivo}
              onChange={handleChange}
              style={{ width: 'auto' }}
            />
            <label htmlFor="attivo" style={{ marginBottom: 0 }}>
              Locale attivo
            </label>
          </div>

          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Annulla
            </button>
            <button type="submit" className="btn btn-primary">
              {locale ? 'Salva Modifiche' : 'Crea Locale'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default LocaleForm
