"use client"

import { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient, QueryClient, QueryClientProvider } from "@tanstack/react-query"
import api from "@/lib/api"
import { ExternalLink, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { AddProfessorDialog } from "@/components/add-professor-dialog"
import { useRouter } from "next/navigation"

// Create a client
const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ProfessorBoard />
    </QueryClientProvider>
  )
}

function ProfessorBoard() {
  const queryClient = useQueryClient()
  const router = useRouter()
  const [isAuthChecking, setIsAuthChecking] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
    } else {
      setIsAuthChecking(false)
    }
  }, [router])

  const { data: professors, isLoading } = useQuery({
    queryKey: ['professors'],
    queryFn: async () => {
      const res = await api.get("/professors/")
      return res.data
    },
    enabled: !isAuthChecking
  })

  // Group professors by status
  const columns = {
    "Draft": professors?.filter((p: any) => p.pipeline_status?.status === "Draft") || [],
    "Sent": professors?.filter((p: any) => p.pipeline_status?.status === "Sent") || [],
    "Replied": professors?.filter((p: any) => p.pipeline_status?.status === "Replied") || [],
    "Meeting": professors?.filter((p: any) => p.pipeline_status?.status === "Meeting") || [],
    "Offer": professors?.filter((p: any) => p.pipeline_status?.status === "Offer") || [],
    "Rejection": professors?.filter((p: any) => p.pipeline_status?.status === "Rejection") || [],
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    router.push("/login")
  }

  if (isAuthChecking) return <div className="min-h-screen flex items-center justify-center">Loading...</div>

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[1920px] mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Professor Outreach</h1>
            <p className="text-slate-500 mt-1">Manage your academic applications and cold emails.</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleLogout} title="Logout">
              <LogOut className="w-4 h-4" />
            </Button>
            <AddProfessorDialog />
          </div>
        </div>

        {/* Board */}
        <div className="flex gap-6 h-[calc(100vh-200px)] overflow-x-auto pb-4 snap-x">
          {Object.entries(columns).map(([status, items]: [string, any[]]) => (
            <div key={status} className="min-w-[320px] w-[350px] bg-slate-100/50 rounded-xl p-4 border border-slate-200/60 flex flex-col snap-start">
              <div className="flex items-center justify-between mb-4 px-2">
                <h3 className="font-semibold text-slate-700 flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${status === 'Draft' ? 'bg-slate-400' :
                    status === 'Sent' ? 'bg-blue-500' :
                      status === 'Replied' ? 'bg-yellow-500' :
                        status === 'Meeting' ? 'bg-purple-500' :
                          status === 'Offer' ? 'bg-green-500' :
                            'bg-red-500'
                    }`} />
                  {status}
                </h3>
                <span className="text-xs text-slate-400 font-medium bg-slate-200 px-2 py-0.5 rounded-full">{items.length}</span>
              </div>

              <div className="space-y-3 overflow-y-auto flex-1 pr-1">
                {items.length === 0 && (
                  <div className="h-full flex items-center justify-center text-slate-400 text-sm border-2 border-dashed border-slate-200 rounded-lg">
                    No professors
                  </div>
                )}
                {items.map((prof) => (
                  <Card key={prof.id} className="cursor-pointer hover:shadow-md transition-shadow group shrink-0">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex justify-between items-start gap-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            {prof.avatar_url ? (
                              <img src={prof.avatar_url} alt={prof.name} className="w-10 h-10 rounded-full object-cover border border-slate-200" />
                            ) : (
                              <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold text-sm">
                                {prof.name.split(" ").map((n: any) => n[0]).join("").substring(0, 2)}
                              </div>
                            )}
                            <div>
                              <h4 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1">{prof.name}</h4>
                              <div className="flex items-center gap-2">
                                <p className="text-xs text-slate-500 line-clamp-1">{prof.affiliation}</p>
                                {prof.target_role && (
                                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${prof.target_role === 'summer_intern' ? 'bg-teal-100 text-teal-700' :
                                      prof.target_role === 'phd' ? 'bg-indigo-100 text-indigo-700' :
                                        prof.target_role === 'postdoc' ? 'bg-purple-100 text-purple-700' :
                                          'bg-orange-100 text-orange-700'
                                    }`}>
                                    {prof.target_role === 'summer_intern' ? 'Summer' :
                                      prof.target_role === 'phd' ? 'PhD' :
                                        prof.target_role === 'ra' ? 'RA' :
                                          prof.target_role}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                        {prof.pipeline_status?.followup_recommended && (
                          <span className="bg-red-100 text-red-600 text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wide shrink-0">
                            Follow-up
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-2">
                        <Button variant="outline" size="sm" className="w-full text-xs h-8" asChild>
                          <a href={prof.website_url} target="_blank" rel="noreferrer">
                            <ExternalLink className="w-3 h-3 mr-1.5" /> Website
                          </a>
                        </Button>
                        <Button variant="secondary" size="sm" className="w-full text-xs h-8" asChild>
                          <a href={`/professors/${prof.id}`}>View Details</a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App
