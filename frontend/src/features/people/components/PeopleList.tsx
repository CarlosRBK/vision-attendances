import { useQuery } from '@tanstack/react-query'
import { getStaticFileUrl } from '@/utils/url'
import { listPeople } from '../api'
import type { Person } from '../types'

export default function PeopleList() {
  const { data: people, isLoading, refetch } = useQuery({
    queryKey: ['people'],
    queryFn: listPeople
  })

  const rows = Array.isArray(people) ? people : []

  const imgSrc = (p: Person) => getStaticFileUrl(p.photo_url, p.updated_at ?? undefined)

  return (
    <div className="rounded-2xl border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-600">Personas</h3>
        <button className="btn" onClick={() => refetch()} disabled={isLoading}>
          {isLoading ? 'Actualizando…' : 'Actualizar'}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-gray-400">
            <tr>
              <th className="py-2 pr-3 w-12">Foto</th>
              <th className="py-2 pr-3">Nombre</th>
              <th className="py-2 px-3">Email</th>
              <th className="py-2 px-3">Grado</th>
              <th className="py-2 px-3">Grupo</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id} className="border-t border-gray-200 hover:bg-gray-100">
                <td className="py-2 pr-3">
                  {imgSrc(p) ? (
                    <img
                      src={imgSrc(p)!}
                      alt={p.full_name}
                      className="size-9 rounded-full object-cover border border-gray-200 bg-gray-200"
                    />
                  ) : (
                    <div className="size-9 rounded-full bg-gray-200 grid place-items-center text-xs text-gray-400">
                      {p.full_name?.charAt(0) || '?'}
                    </div>
                  )}
                </td>
                <td className="py-2 pr-3 font-medium">{p.full_name}</td>
                <td className="py-2 px-3">{p.email || '-'}</td>
                <td className="py-2 px-3">{p.grade || '-'}</td>
                <td className="py-2 px-3">{p.group || '-'}</td>
              </tr>
            ))}
            {!isLoading && rows.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-center text-gray-400">
                  Sin registros aún
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
