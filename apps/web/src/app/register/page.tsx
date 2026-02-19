"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import axios from "axios"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { API_URL } from "@/lib/config"

import { toast } from "sonner"

export default function RegisterPage() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [loading, setLoading] = useState(false)
    const router = useRouter()

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError("")

        try {
            await axios.post(`${API_URL}/users/`, {
                email,
                password
            })
            toast.success("Account created successfully!", {
                description: "Redirecting to login...",
                duration: 2000,
            })
            setTimeout(() => {
                router.push("/login")
            }, 1500)
        } catch (err: any) {
            console.error(err)
            if (err.response?.status === 400) {
                setError("Email already registered")
            } else if (err.response?.data?.detail) {
                setError(`Registration failed: ${err.response.data.detail}`)
            } else {
                setError("Registration failed. Check network or server logs.")
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle>Create Account</CardTitle>
                    <CardDescription>Start tracking your academic applications.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleRegister} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Email</label>
                            <Input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="you@example.com"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Password</label>
                            <Input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                minLength={6}
                            />
                        </div>

                        {error && <p className="text-sm text-red-500">{error}</p>}

                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? "Creating Account..." : "Register"}
                        </Button>

                        <div className="text-center text-sm text-slate-500">
                            Already have an account? <a href="/login" className="text-blue-600 hover:underline">Login</a>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
