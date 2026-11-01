import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { z } from 'zod';

import { useCreateRun } from '../hooks';
import { Button, Card, Input } from '@/components/ui';
import { ROUTES } from '@/constants/routes';
import { errorMessage } from '@/lib/http';
import type { AnomalyType } from '@/types/enums';

const ANOMALIES: AnomalyType[] = ['capacity_exceeded', 'stop_omitted', 'stop_duplicated', 'arrival_before_departure', 'shift_exceeded', 'coordinate_out_of_region'];
const PRESETS = { starter: { sites: 50, deliveries: 200, vehicles: 10, days: 3 }, full: { sites: 500, deliveries: 2000, vehicles: 100, days: 30 } };

const schema = z.object({
  name: z.string().min(2),
  seed: z.coerce.number().int(),
  sites: z.coerce.number().int().min(1),
  deliveries: z.coerce.number().int().min(1),
  vehicles: z.coerce.number().int().min(1),
  days: z.coerce.number().int().min(1).max(366),
  anomaly_rate: z.coerce.number().min(0).max(0.2),
});
type Form = z.infer<typeof schema>;

export default function NewRunPage() {
  const navigate = useNavigate();
  const create = useCreateRun();
  const { register, handleSubmit, reset, getValues, formState: { errors } } = useForm<Form>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', seed: 20261022, ...PRESETS.full, anomaly_rate: 0.02 },
  });
  const onSubmit = ({ sites, deliveries, vehicles, days, ...rest }: Form) =>
    create.mutate({ ...rest, scale: { sites, deliveries, vehicles, days }, anomaly_types: ANOMALIES },
      { onSuccess: (r) => navigate(ROUTES.run(r.run_id)) });

  return (
    <Card title="New generation run">
      <form onSubmit={handleSubmit(onSubmit)} className="grid max-w-xl grid-cols-2 gap-4">
        <div className="col-span-2 flex gap-2">
          {(Object.keys(PRESETS) as (keyof typeof PRESETS)[]).map((k) => (
            <Button key={k} type="button" variant="secondary" onClick={() => reset({ ...getValues(), ...PRESETS[k] })}>{k} preset</Button>))}
        </div>
        <div className="col-span-2"><Input label="Name" {...register('name')} error={errors.name?.message} /></div>
        <Input label="Seed" type="number" {...register('seed')} />
        <Input label="Anomaly rate (0–0.2)" type="number" step="0.005" {...register('anomaly_rate')} error={errors.anomaly_rate?.message} />
        <Input label="Sites" type="number" {...register('sites')} />
        <Input label="Deliveries" type="number" {...register('deliveries')} />
        <Input label="Vehicles" type="number" {...register('vehicles')} />
        <Input label="Days" type="number" {...register('days')} />
        {create.isError && <p className="col-span-2 text-sm text-red-600">{errorMessage(create.error)}</p>}
        <Button type="submit" className="col-span-2" disabled={create.isPending}>Generate</Button>
      </form>
    </Card>
  );
}
