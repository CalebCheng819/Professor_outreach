"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { useQuery, useMutation, useQueryClient, QueryClient, QueryClientProvider } from "@tanstack/react-query"
import axios from "axios"
import { ArrowLeft, ExternalLink, RefreshCw, Sparkles, FileText, Mail, StickyNote } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { toast } from "sonner"

const API_URL = "http://localhost:8000"

const queryClient = new QueryClient()

function ProfessorDetailWrapper() {
    return (
        <QueryClientProvider client={queryClient}>
            <ProfessorDetail />
        </QueryClientProvider>
    )
}

function ProfessorDetail() {
    const params = useParams()
    const id = params.id
    const queryClient = useQueryClient()
    const [activeTab, setActiveTab] = useState("card")

    // Fetch Professor Data
    const { data: professor, isLoading, error } = useQuery({
        queryKey: ['professor', id],
        queryFn: async () => {
            const res = await axios.get(`${API_URL}/professors/${id}`)
            return res.data
        }
    })

    // ...

    // Ingest Mutation
    const ingestMutation = useMutation({
        mutationFn: async () => {
            const toastId = toast.loading("Fetching website...")
            try {
                await axios.post(`${API_URL}/ingest`, {
                    professor_id: parseInt(id as string),
                    url: professor.website_url
                })
                toast.success("Website ingested successfully!", { id: toastId })
            } catch (err: any) {
                toast.error("Ingestion failed: " + err.message, { id: toastId })
                throw err
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['professor', id] })
        }
    })

    // Generate Card Mutation
    const generateCardMutation = useMutation({
        mutationFn: async () => {
            const toastId = toast.loading("Generating card...")
            try {
                await axios.post(`${API_URL}/professors/${id}/generate-card`)
                toast.success("Card generated!", { id: toastId })
            } catch (err: any) {
                toast.error("Card generation failed: " + err.message, { id: toastId })
                throw err
            }
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['professor', id] })
        }
    })

    if (isLoading) return <div className="p-8">Loading...</div>
    if (error) return <div className="p-8">Error loading professor</div>
    if (!professor) return <div className="p-8">Professor not found</div>

    const latestCard = professor.professor_cards && professor.professor_cards.length > 0
        ? professor.professor_cards[professor.professor_cards.length - 1]
        : null;

    const cardData = latestCard ? JSON.parse(latestCard.card_json) : null;

    return (
        <div className="min-h-screen bg-slate-50 p-8">
            <div className="max-w-5xl mx-auto space-y-6">
                {/* Navigation */}
                <Link href="/">
                    <Button variant="ghost" className="pl-0 gap-2 text-slate-500 hover:text-slate-900">
                        <ArrowLeft className="w-4 h-4" /> Back to Board
                    </Button>
                </Link>

                {/* Header */}
                <div className="bg-white rounded-xl p-6 border shadow-sm flex justify-between items-start">
                    <div>
                        <div>
                            <h1 className="text-3xl font-bold text-slate-900">{professor.name}</h1>
                            <p className="text-lg text-slate-500">{professor.affiliation}</p>
                            <div className="flex items-center gap-4 mt-2">
                                <a href={professor.website_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline text-sm flex items-center">
                                    <ExternalLink className="w-3 h-3 mr-1" /> {professor.website_url}
                                </a>
                                <div className="flex items-center gap-2">
                                    <Label className="text-xs text-slate-400">Status:</Label>
                                    <select
                                        className="text-sm border rounded px-2 py-1 bg-slate-50"
                                        value={professor.pipeline_status?.status || "Draft"}
                                        onChange={(e) => {
                                            const newStatus = e.target.value;
                                            axios.patch(`${API_URL}/professors/${id}/status`, { status: newStatus })
                                                .then(() => queryClient.invalidateQueries({ queryKey: ['professor', id] }))
                                                .catch(err => alert("Failed to update status"));
                                        }}
                                    >
                                        <option value="Draft">Draft</option>
                                        <option value="Sent">Sent</option>
                                        <option value="Replied">Replied</option>
                                        <option value="Rejected">Rejected</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" onClick={() => ingestMutation.mutate()} disabled={ingestMutation.isPending}>
                            <RefreshCw className={`w-4 h-4 mr-2 ${ingestMutation.isPending ? 'animate-spin' : ''}`} />
                            {ingestMutation.isPending ? 'Fetching...' : 'Fetch Website'}
                        </Button>
                        <Button onClick={() => generateCardMutation.mutate()} disabled={generateCardMutation.isPending}>
                            <Sparkles className="w-4 h-4 mr-2" />
                            {generateCardMutation.isPending ? 'Generating...' : 'Generate Card'}
                        </Button>
                    </div>
                </div>

                {/* Content Tabs */}
                <Tabs defaultValue="card" className="w-full" onValueChange={setActiveTab}>
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="card" className="gap-2"><FileText className="w-4 h-4" /> Professor Card</TabsTrigger>
                        <TabsTrigger value="emails" className="gap-2"><Mail className="w-4 h-4" /> Emails</TabsTrigger>
                        <TabsTrigger value="notes" className="gap-2"><StickyNote className="w-4 h-4" /> Notes</TabsTrigger>
                    </TabsList>

                    <TabsContent value="card" className="mt-6">
                        <div className="grid grid-cols-3 gap-6">
                            {/* Left Column: Structured Data */}
                            <div className="col-span-1 space-y-6">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">Research Interests</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        {cardData && cardData.research_interests.length > 0 ? (
                                            <div className="flex flex-wrap gap-2">
                                                {cardData.research_interests.map((interest: string, i: number) => (
                                                    <span key={i} className="bg-blue-50 text-blue-700 px-2 py-1 rounded-md text-sm font-medium">
                                                        {interest}
                                                    </span>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-sm text-slate-400 italic">No interests extracted.</p>
                                        )}
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-base">Quick Stats</CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-slate-500">Source Fetched</span>
                                            <span className="font-medium">{professor.source_pages?.length > 0 ? 'Yes' : 'No'}</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-slate-500">Card Version</span>
                                            <span className="font-medium">{latestCard ? `v${latestCard.version}` : '-'}</span>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            {/* Right Column: Markdown Content */}
                            <div className="col-span-2">
                                <Card className="h-full">
                                    <CardHeader>
                                        <CardTitle>Professor Summary</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        {latestCard ? (
                                            <div className="prose prose-sm max-w-none dark:prose-invert">
                                                <div className="whitespace-pre-wrap font-sans text-slate-700 leading-relaxed">
                                                    {latestCard.card_md}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex flex-col items-center justify-center h-64 text-slate-400 border-2 border-dashed rounded-lg bg-slate-50">
                                                <Sparkles className="w-8 h-8 mb-2 opacity-50" />
                                                <p>No card generated yet.</p>
                                                <Button variant="link" onClick={() => generateCardMutation.mutate()} className="mt-2">
                                                    Generate now
                                                </Button>
                                            </div>
                                        )}
                                    </CardContent>
                                </Card>
                            </div>
                        </div>
                    </TabsContent>

                    <TabsContent value="emails" className="mt-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <Card className="col-span-1">
                                <CardHeader>
                                    <CardTitle>Generate Draft</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <p className="text-sm text-slate-500">
                                        Generate a personalization draft using extracted interests.
                                    </p>
                                    <div className="space-y-2">
                                        <Label>Template</Label>
                                        <select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" id="template-select">
                                            <option value="summer_intern">Summer Internship</option>
                                            <option value="phd_inquiry">Ph.D. Inquiry</option>
                                        </select>
                                    </div>
                                    <Button className="w-full" onClick={() => {
                                        const template = (document.getElementById('template-select') as HTMLSelectElement).value;
                                        const promise = axios.post(`${API_URL}/professors/${id}/generate-email?template=${template}`);
                                        promise.then(() => {
                                            queryClient.invalidateQueries({ queryKey: ['professor', id] });
                                            alert("Draft generated!");
                                        }).catch(err => alert("Failed: " + err.message));
                                    }}>
                                        <Sparkles className="w-4 h-4 mr-2" /> Generate Draft
                                    </Button>
                                </CardContent>
                            </Card>

                            <div className="col-span-2 space-y-4">
                                {professor.email_drafts && professor.email_drafts.length > 0 ? (
                                    professor.email_drafts.slice().reverse().map((draft: any) => (
                                        <Card key={draft.id}>
                                            <CardHeader className="pb-2">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{draft.type}</p>
                                                        <CardTitle className="text-lg mt-1">{draft.subject}</CardTitle>
                                                    </div>
                                                    <span className="text-xs text-slate-400">
                                                        {new Date(draft.created_at).toLocaleDateString()}
                                                    </span>
                                                </div>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="bg-slate-50 p-4 rounded-md whitespace-pre-wrap text-sm text-slate-700 font-mono border">
                                                    {draft.body}
                                                </div>
                                                <div className="flex justify-end gap-2 mt-4">
                                                    <Button variant="outline" size="sm" onClick={() => {
                                                        navigator.clipboard.writeText(`${draft.subject}\n\n${draft.body}`);
                                                        alert("Copied to clipboard!");
                                                    }}>
                                                        Copy to Clipboard
                                                    </Button>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-64 text-slate-400 border-2 border-dashed rounded-lg bg-slate-50">
                                        <Mail className="w-8 h-8 mb-2 opacity-50" />
                                        <p>No email drafts yet.</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </TabsContent>

                    <TabsContent value="notes" className="mt-6">
                        <Card>
                            <CardContent className="h-64 flex items-center justify-center text-slate-400">
                                Notes coming soon.
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div>
    )
}

export default ProfessorDetailWrapper
