import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/uk');
  return null;
}
