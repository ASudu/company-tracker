import React from 'react'

export default function NewsList({items}) {
  if (!items || items.length === 0) return <div className="text-slate-400">No items found.</div>
  return (
    <ul className="space-y-3">
      {items.map((it, idx) => (
        <li key={idx} className="card">
          <a href={it.link} target="_blank" rel="noreferrer" className="font-semibold text-white hover:underline">{it.title}</a>
          <div className="text-sm text-slate-300 mt-1">{it.summary ? stripHtml(it.summary).slice(0, 240) : ''}</div>
          <div className="text-xs text-slate-400 mt-2">{it.published ? new Date(it.published).toLocaleString() : ''} • {it.source || ''}</div>
        </li>
      ))}
    </ul>
  )
}

function stripHtml(s=''){
  return s.replace(/<\/?[^>]+(>|$)/g, "");
}