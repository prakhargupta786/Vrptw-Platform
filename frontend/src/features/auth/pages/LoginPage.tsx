import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useLocation } from 'react-router-dom';
import { z } from 'zod';

import { useLogin } from '../hooks';
import { Button, Input } from '@/components/ui';
import { ROUTES } from '@/constants/routes';
import { errorMessage } from '@/lib/http';

const schema = z.object({ email: z.string().email(), password: z.string().min(8) });
type Form = z.infer<typeof schema>;

export default function LoginPage() {
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? ROUTES.dashboard;
  const login = useLogin(from);
  const { register, handleSubmit, formState: { errors } } = useForm<Form>({ resolver: zodResolver(schema) });

  return (
    <form onSubmit={handleSubmit((v) => login.mutate(v))} className="space-y-4">
      <h1 className="text-xl font-semibold">Sign in</h1>
      <Input label="Email" type="email" {...register('email')} error={errors.email?.message} />
      <Input label="Password" type="password" {...register('password')} error={errors.password?.message} />
      {login.isError && <p className="text-sm text-red-600">{errorMessage(login.error)}</p>}
      <Button type="submit" className="w-full" disabled={login.isPending}>{login.isPending ? 'Signing in…' : 'Sign in'}</Button>
    </form>
  );
}
