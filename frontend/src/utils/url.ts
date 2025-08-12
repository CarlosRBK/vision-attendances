/**
 * Constructs a full URL for a static file hosted on the backend.
 * @param path The relative path to the file (e.g., /static/image.png).
 * @param cacheKey An optional key to append as a query parameter for cache-busting.
 * @returns The full URL as a string, or null if the path is not provided.
 */
export function getStaticFileUrl(path: string | null | undefined, cacheKey?: string): string | null {
  if (!path) return null

  try {
    // Use the backend URL as the base for resolving the static file path.
    const backendUrl = new URL(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
    const staticUrl = new URL(path, backendUrl.origin)

    // Add a cache-busting parameter if provided.
    if (cacheKey) {
      staticUrl.searchParams.set('v', cacheKey)
    }

    return staticUrl.href
  } catch (error) {
    console.error('Error creating static file URL:', error)
    return path // Fallback to the original path if URL construction fails.
  }
}
