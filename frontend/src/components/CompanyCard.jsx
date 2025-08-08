import React from 'react'

export default function CompanyCard({c, onOpen}) {
  return (
    <div className="card hover:scale-[1.02] transition-transform cursor-pointer" onClick={() => onOpen(c)}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">{c.name}</div>
          <div className="text-sm text-slate-300">{c.ticker || ''}</div>
        </div>
        <div className="text-xs text-slate-400">Updated: {new Date(c.last_updated).toLocaleString()}</div>
      </div>
    </div>
  )
}