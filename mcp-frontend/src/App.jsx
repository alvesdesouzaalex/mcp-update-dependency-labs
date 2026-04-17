import { useState } from 'react'
import './App.css'

function App() {
  const [name, setName] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim()) return

    setLoading(true)
    setError('')
    setResponse('')

    try {
      const res = await fetch(`http://localhost:8080/hello?name=${encodeURIComponent(name)}`)
      if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`)
      const text = await res.text()
      setResponse(text)
    } catch (err) {
      setError('Não foi possível conectar ao backend. Certifique-se de que está rodando na porta 8080.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <div className="icon">👋</div>
          <h1>MCP Hello</h1>
          <p className="subtitle">Digite seu nome e diga olá ao servidor</p>
        </div>

        <form onSubmit={handleSubmit} className="form">
          <div className="input-group">
            <label htmlFor="name-input">Seu Nome</label>
            <input
              id="name-input"
              type="text"
              placeholder="Ex: Alex"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={loading}
              autoComplete="off"
            />
          </div>

          <button
            type="submit"
            className={`btn ${loading ? 'loading' : ''}`}
            disabled={loading || !name.trim()}
          >
            {loading ? (
              <>
                <span className="spinner" />
                Enviando...
              </>
            ) : (
              'Enviar ao Servidor →'
            )}
          </button>
        </form>

        {response && (
          <div className="result success">
            <div className="result-label">✅ Resposta do Backend</div>
            <div className="result-text">{response}</div>
          </div>
        )}

        {error && (
          <div className="result error">
            <div className="result-label">❌ Erro</div>
            <div className="result-text">{error}</div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
