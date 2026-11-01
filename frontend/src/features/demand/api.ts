import { http } from '@/lib/http';
import type { Delivery, Order, Outcome, TimeWindow } from '@/types/entities';
import type { OrderStatus, Priority, VehicleType, WindowType } from '@/types/enums';

export interface OrderCreate { site_id: string; quantity: number; weight_kg: number; volume_m3: number; priority: Priority }
export interface TimeWindowIn { earliest: string; latest: string; type: WindowType; priority: number }
export interface DeliveryCreate { service_minutes: number; required_vehicle_type: VehicleType; time_window: TimeWindowIn }
export interface OrderDetail extends Order { deliveries: Delivery[]; outcomes: Outcome[] }

export const demandApi = {
  createOrder: async (runId: string, body: OrderCreate) => (await http.post<Order>(`/runs/${runId}/orders`, body)).data,
  transition: async (runId: string, orderId: string, to_status: OrderStatus, reason?: string) =>
    (await http.post<Order>(`/runs/${runId}/orders/${orderId}/transition`, { to_status, reason })).data,
  createDelivery: async (runId: string, orderId: string, body: DeliveryCreate) =>
    (await http.post<Delivery>(`/runs/${runId}/orders/${orderId}/deliveries`, body)).data,
  setTimeWindow: async (runId: string, deliveryId: string, body: TimeWindowIn) =>
    (await http.put<TimeWindow>(`/runs/${runId}/deliveries/${deliveryId}/time-window`, body)).data,
};
