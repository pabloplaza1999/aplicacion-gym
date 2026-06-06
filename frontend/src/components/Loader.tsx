export function Loader() {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-6 h-6 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
    </div>
  )
}

export function ErrorMsg({ message }: { message: string }) {
  return (
    <div className="card p-4 border-red-900 bg-red-950/30 text-red-400 text-sm">
      {message}
    </div>
  )
}
