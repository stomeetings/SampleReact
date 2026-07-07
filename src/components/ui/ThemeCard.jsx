function ThemeCard({ title, children }) {
  return (
    <div className="theme-card">
      <h2>{title}</h2>
      {children}
    </div>
  )
}

export default ThemeCard
