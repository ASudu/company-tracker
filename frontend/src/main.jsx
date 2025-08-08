import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles/index.css'
import { HashRouter } from 'react-router-dom'

createRoot(document.getElementById('root')).render(
  <HashRouter>
    <App />
  </HashRouter>
)