export function HelpModal({open, onClose}: {open: boolean; onClose: ()=>void}) {
  if (!open) return null
  return <div className="modal-backdrop" onClick={onClose}>
    <div className="modal" onClick={e => e.stopPropagation()}>
      <h3>What does this mean?</h3>
      <p>FloodPulse shows recent gauge observations and whether water levels are rising or falling quickly.</p>
      <p>Rising fast means the last hour changed above a threshold. It is not a flood forecast.</p>
      <p>Always follow local emergency services for warnings.</p>
      <button onClick={onClose}>Close</button>
    </div>
  </div>
}
