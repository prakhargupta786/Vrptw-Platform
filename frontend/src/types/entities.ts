import type {
  AnomalyType, DeliveryStatus, JobStatus, OrderStatus, OutcomeStatus, Priority, ReasonCode, Role,
  RunStatus, ValidationCheck, VehicleStatus, VehicleType, WindowType,
} from './enums';

export interface User {
  id: string; email: string; name: string; role: Role; supplier_id: string | null; is_active: boolean;
}
export interface Me extends User { permissions: string[] }

export interface Scale { sites: number; deliveries: number; vehicles: number; days: number }
export interface Run {
  id: string; name: string; seed: number; status: RunStatus; created_at: string; locked_at: string | null;
  config: { scale: Scale; anomaly_rate: number; anomaly_types: AnomalyType[] };
  row_counts: Record<string, number> | null;
}
export interface Job {
  id: string; run_id: string; kind: string; status: JobStatus; step: string | null; progress: number;
  result: Record<string, unknown> | null; error: string | null;
}

export interface Site {
  site_id: string; name: string; lat: number; lon: number; region: string; address_type: string;
  access_restrictions: { max_vehicle_type?: VehicleType; zone?: string };
}
export interface Vehicle {
  vehicle_id: string; type: VehicleType; status: VehicleStatus; restricted_zones: string[];
  effective_from: string; effective_to: string | null;
}
export interface VehicleCapacity {
  capacity_id: string; vehicle_id: string; max_weight_kg: number; max_volume_m3: number; max_stops: number;
  effective_from: string; effective_to: string | null;
}
export interface Driver { driver_id: string; name: string; license_class: string; home_depot: string; is_active: boolean }
export interface Shift {
  shift_id: string; driver_id: string; start_at: string; end_at: string; break_minutes: number; max_driving_hours: number;
}

export interface Order {
  order_id: string; site_id: string; supplier_id: string | null; quantity: number; weight_kg: number;
  volume_m3: number; priority: Priority; status: OrderStatus; created_at: string;
}
export interface Delivery {
  delivery_id: string; order_id: string; service_minutes: number; required_vehicle_type: VehicleType;
  weight_kg: number; volume_m3: number; status: DeliveryStatus;
}
export interface TimeWindow {
  window_id: string; delivery_id: string; earliest: string; latest: string; type: WindowType; priority: number;
}

export interface Route {
  route_id: string; route_date: string; vehicle_id: string; driver_id: string; shift_id: string;
  total_weight_kg: number; total_volume_m3: number; total_distance_km: number; planned_duration_min: number;
  flags: string[];
}
export interface RouteStop {
  stop_id: string; route_id: string; delivery_id: string; sequence: number; planned_arrival: string;
  planned_departure: string; travel_km_from_prev: number; removed_at: string | null;
}
export interface RouteDetail extends Route {
  stops: RouteStop[];
  capacity: Pick<VehicleCapacity, 'max_weight_kg' | 'max_volume_m3' | 'max_stops'>;
  utilization: { weight_pct: number; volume_pct: number; stops_pct: number };
}
export interface Unserved { delivery_id: string; reason: ReasonCode }

export interface Outcome {
  outcome_id: string; delivery_id: string; stop_id: string | null; actual_arrival: string | null;
  actual_departure: string | null; status: OutcomeStatus; reason_code: ReasonCode | null; delay_minutes: number;
}

export interface GroundTruth { issue_type: AnomalyType; affected_entity: string; affected_id: string; expected_decision: string }
export interface DetectedAnomaly { check: ValidationCheck; detected_type: string | null; affected_id: string }
export interface CheckResult { name: ValidationCheck; status: 'pass' | 'fail'; failed_rows: number; sample_ids: string[] }
export interface ValidationSummary { passed: number; failed: number; checks: CheckResult[]; at: string | null }

export interface Kpis {
  on_time_rate: number; failed_rate: number; avg_delay_min: number; unserved_count: number;
  total_distance_km: number; total_travel_min: number; overtime_count: number;
}
export interface DetectionScore {
  issue_type: AnomalyType; tp: number; fp: number; fn: number; precision: number; recall: number;
}
export interface Export {
  id: string; formats: string[]; include: string[]; size_bytes: number | null; sha256: string | null; created_at: string;
}
