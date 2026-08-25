import React from 'react';

export function Input({ label, id, error, ...props }) {
  return (
    <div style={{ marginBottom: 12 }}>
      {label && <label htmlFor={id} className="small">{label}</label>}
      <input id={id} className="input" aria-invalid={!!error} {...props} />
      {error && <div role="alert" style={{ color: '#d14343', marginTop: 6 }}>{error}</div>}
    </div>
  );
}
