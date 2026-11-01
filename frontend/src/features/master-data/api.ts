import { http } from '@/lib/http';
import type { Shift, Site, Vehicle, VehicleCapacity } from '@/types/entities';
import type { TrafficScenario } from '@/types/enums';

export interface CapacityIn { max_weight_kg: number; max_volume_m3: number; max_stops: number; effective_from: string }
export interface ShiftIn { start_at: string; end_at: string; break_minutes: number; max_driving_hours: number }
export interface TravelLookup { from_site: string; to_site: string; day: number; scenario: TrafficScenario; distance_km: number; traffic_factor: number; travel_minutes: number }

// Lists use the generic useRunList(runId, 'sites' | 'vehicles' | 'drivers', filters).
export const masterApi = {
  updateSite: async (runId: string, siteId: string, body: Partial<Pick<Site, 'lat' | 'lon' | 'access_restrictions'>>) =>
    (await http.patch<Site>(`/runs/${runId}/sites/${siteId}`, body)).data,
  updateVehicle: async (runId: string, vehicleId: string, body: Partial<Pick<Vehicle, 'status' | 'restricted_zones'>>) =>
    (await http.patch<Vehicle>(`/runs/${runId}/vehicles/${vehicleId}`, body)).data,
  capacities: async (runId: string, vehicleId: string, at?: string) =>
    (await http.get<VehicleCapacity[]>(`/runs/${runId}/vehicles/${vehicleId}/capacities`, { params: at ? { at } : {} })).data,
  addCapacity: async (runId: string, vehicleId: string, body: CapacityIn) =>
    (await http.post<VehicleCapacity>(`/runs/${runId}/vehicles/${vehicleId}/capacities`, body)).data,
  shifts: async (runId: string, driverId: string) => (await http.get<Shift[]>(`/runs/${runId}/drivers/${driverId}/shifts`)).data,
  addShift: async (runId: string, driverId: string, body: ShiftIn) =>
    (await http.post<Shift>(`/runs/${runId}/drivers/${driverId}/shifts`, body)).data,
  travelLookup: async (runId: string, q: { from_site: string; to_site: string; day: number; scenario: TrafficScenario }) =>
    (await http.get<TravelLookup>(`/runs/${runId}/travel-matrix/lookup`, { params: q })).data,
};
