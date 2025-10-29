import { useState, useEffect } from 'react'
import axios from 'axios'
import LocaleList from './components/LocaleList'
import LocaleForm from './components/LocaleForm'

const API_URL = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [locali, setLocali] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [editingLocale, setEditingLocale] = useState(null)

  // Carica i locali all'avvio
  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [localiRes, statsRes] = await Promise.all([
        axios.get(`${API_URL}/locali`),
        axios.get(`${API_URL}/stats`)
      ])

      setLocali(localiRes.data)
      setStats(statsRes.data)
    } catch (err) {
      setError('Errore nel caricamento dei dati')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateLocale = async (localeData) => {
    try {
      await axios.post(`${API_URL}/locali`, localeData)
      await loadData()
      setShowForm(false)
      setEditingLocale(null)
    } catch (err) {
      alert('Errore nella creazione del locale: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleUpdateLocale = async (localeId, localeData) => {
    try {
      await axios.put(`${API_URL}/locali/${localeId}`, localeData)
      await loadData()
      setShowForm(false)
      setEditingLocale(null)
    } catch (err) {
      alert('Errore nell\'aggiornamento del locale: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleDeleteLocale = async (localeId) => {
    if (!confirm('Sei sicuro di voler eliminare questo locale?')) return

    try {
      await axios.delete(`${API_URL}/locali/${localeId}`)
      await loadData()
    } catch (err) {
      alert('Errore nell\'eliminazione del locale: ' + (err.response?.data?.error || err.message))
    }
  }

  const handleEditLocale = (locale) => {
    setEditingLocale(locale)
    setShowForm(true)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingLocale(null)
  }

  if (loading) {
    return (
      <div className="loading">
        <h2>Caricamento...</h2>
      </div>
    )
  }

  return (
    <div>
      <div className="header">
        <h1>🍕 Pratico Dashboard</h1>
        <p>Gestione Locali & Automazione Download</p>
      </div>

      <div className="container">
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {stats && (
          <div className="stats">
            <div className="stat-card">
              <h3>{stats.totale_locali}</h3>
              <p>Totale Locali</p>
            </div>
            <div className="stat-card">
              <h3>{stats.locali_attivi}</h3>
              <p>Locali Attivi</p>
            </div>
            <div className="stat-card">
              <h3>{stats.ultimi_logs?.length || 0}</h3>
              <p>Ultimi Log</p>
            </div>
          </div>
        )}

        <div className="dashboard">
          <div className="actions">
            <h2>I Tuoi Locali</h2>
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              ➕ Aggiungi Locale
            </button>
          </div>

          <LocaleList
            locali={locali}
            onEdit={handleEditLocale}
            onDelete={handleDeleteLocale}
          />
        </div>
      </div>

      {showForm && (
        <LocaleForm
          locale={editingLocale}
          onSubmit={editingLocale ?
            (data) => handleUpdateLocale(editingLocale.id, data) :
            handleCreateLocale
          }
          onClose={handleCloseForm}
        />
      )}
    </div>
  )
}

export default App
