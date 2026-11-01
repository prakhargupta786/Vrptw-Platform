export type Role = 'ADMIN' | 'PLANNER' | 'WAREHOUSE' | 'ANALYST' | 'OPS_MANAGER' | 'SUPPLIER';
export type RunStatus = 'queued' | 'generating' | 'ready' | 'validating' | 'validated' | 'locked' | 'failed';
export type JobStatus = 'queued' | 'running' | 'succeeded' | 'failed';
export type VehicleType = 'mini' | 'van' | 'truck';
export type VehicleStatus = 'active' | 'maintenance' | 'retired';
export type OrderStatus = 'created' | 'planned' | 'completed' | 'cancelled';
export type Priority = 'low' | 'normal' | 'high';
export type DeliveryStatus = 'pending' | 'assigned' | 'unserved' | 'done';
export type WindowType = 'hard' | 'soft';
export type OutcomeStatus = 'delivered' | 'late' | 'failed' | 'skipped';
export type TrafficScenario = 'peak' | 'off_peak' | 'disruption';
export type ReasonCode =
  | 'CUSTOMER_ABSENT' | 'ACCESS_RESTRICTED' | 'OUTSIDE_WINDOW' | 'NO_CAPACITY'
  | 'NO_VEHICLE_TYPE' | 'SHIFT_LIMIT' | 'REPLANNED';
export type AnomalyType =
  | 'capacity_exceeded' | 'stop_omitted' | 'stop_duplicated'
  | 'arrival_before_departure' | 'shift_exceeded' | 'coordinate_out_of_region';
export type ValidationCheck =
  | 'pk_unique' | 'fk_integrity' | 'enum_values' | 'datetime_order'
  | 'arithmetic' | 'lifecycle' | 'duplicates' | 'anomaly_match';
