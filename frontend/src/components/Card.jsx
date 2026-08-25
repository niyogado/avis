import React from 'react';

export function Card({ title, children, className = '' }) {
  return (
    <section className={`card ${className}`} aria-labelledby={title ? `${title}-title` : undefined}>
      {title && <div className="header-row"><h3 id={`${title}-title`} className="h1">{title}</h3></div>}
      <div>{children}</div>
    </section>
  );
}
