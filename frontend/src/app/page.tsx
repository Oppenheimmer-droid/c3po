import { redirect } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

export default function Home() {
  redirect('/auth/login')
}