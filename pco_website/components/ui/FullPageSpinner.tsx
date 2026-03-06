export function FullPageSpinner() {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center">
      <div
        className="w-8 h-8 rounded-full border border-white/20 border-t-white animate-spin"
        role="status"
        aria-label="Loading"
      />
    </div>
  );
}
