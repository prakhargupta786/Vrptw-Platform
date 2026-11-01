import { CircleMarker, MapContainer, Polyline, TileLayer, Tooltip } from 'react-leaflet';

export interface MapPoint { id: string; lat: number; lon: number; label: string; flagged?: boolean }

/** Sites as markers; when `path` is true the points are joined in order (route stop sequence). */
export function RouteMap({ points, path = false }: { points: MapPoint[]; path?: boolean }) {
  if (!points.length) return null;
  const center: [number, number] = [points[0].lat, points[0].lon];
  return (
    <MapContainer center={center} zoom={12} className="h-96 w-full rounded-lg">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
      {path && <Polyline positions={points.map((p) => [p.lat, p.lon] as [number, number])} />}
      {points.map((p) => (
        <CircleMarker key={p.id} center={[p.lat, p.lon]} radius={6} pathOptions={{ color: p.flagged ? '#dc2626' : '#2563eb' }}>
          <Tooltip>{p.label}</Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
