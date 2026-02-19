"use client"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient, QueryClient, QueryClientProvider } from "@tanstack/react-query"
import axios from "axios"
import { ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { AddProfessorDialog } from "@/components/add-professor-dialog"

const API_URL = "http://localhost:8000"

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

  const { data: professors, isLoading } = useQuery({
    queryKey: ['professors'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/professors/`)
      return res.data
    }
  })

  // Group professors by status
  const columns = {
    "Draft": professors?.filter((p: any) => p.pipeline_status?.status === "Draft") || [],
    "Sent": professors?.filter((p: any) => p.pipeline_status?.status === "Sent") || [],
    "Replied": professors?.filter((p: any) => p.pipeline_status?.status === "Replied") || [],
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">Professor Outreach</h1>
            <p className="text-slate-500 mt-1">Manage your academic applications and cold emails.</p>
          </div>
          <AddProfessorDialog />
        </div>

        {/* Board */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
          {Object.entries(columns).map(([status, items]: [string, any[]]) => (
            <div key={status} className="bg-slate-100/50 rounded-xl p-4 border border-slate-200/60 flex flex-col">
              <div className="flex items-center justify-between mb-4 px-2">
                <h3 className="font-semibold text-slate-700 flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${status === 'Draft' ? 'bg-slate-400' : status === 'Sent' ? 'bg-blue-500' : 'bg-green-500'}`} />
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
                  <Card key={prof.id} className="cursor-pointer hover:shadow-md transition-shadow group">
                    <CardContent className="p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">{prof.name}</h4>
                          <p className="text-sm text-slate-500 line-clamp-1">{prof.affiliation}</p>
                        </div>
                        {prof.pipeline_status?.followup_recommended && (
                          <span className="bg-red-100 text-red-600 text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wide">
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
