"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useQuery, useMutation, useQueryClient, QueryClient, QueryClientProvider } from "@tanstack/react-query"
import api from "@/lib/api"
import { ArrowLeft, ExternalLink, RefreshCw, Sparkles, FileText, Mail, StickyNote, Loader2, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { toast } from "sonner"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"

const queryClient = new QueryClient()

function ProfessorDetailWrapper() {
    return (
        <QueryClientProvider client={queryClient}>
            <ProfessorDetail />
        </QueryClientProvider>
    )
}

export default ProfessorDetailWrapper

function ProfessorDetail() {
    const params = useParams()
    const id = params.id
    const router = useRouter()
    const queryClient = useQueryClient()
    const [activeTab, setActiveTab] = useState("card")

    // Fetch Professor Data
    const { data: professor, isLoading, error } = useQuery({
        queryKey: ['professor', id],
        queryFn: async () => {
            const res = await api.get(`/professors/${id}`)
            return res.data
        }
    })

    // Ingest Mutation
    const ingestMutation = useMutation({
        mutationFn: async (vars?: any) => {
            const toastId = toast.loading("Fetching website...")
            try {
                await api.post("/ingest", {
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

    // Email State & Mutation
    const [emailDraft, setEmailDraft] = useState<any>(null)
    const [emailSettings, setEmailSettings] = useState({
        template: "summer_intern",
        tone: "formal",
        length: "medium",
        customInstructions: ""
    })

    // Update default template when professor data loads
    const [templateInitialized, setTemplateInitialized] = useState(false)
    if (professor?.target_role && !templateInitialized) {
        setEmailSettings(s => ({ ...s, template: professor.target_role }))
        setTemplateInitialized(true)
    }

    const emailMutation = useMutation({
        mutationFn: async () => {
            const toastId = toast.loading("Drafting email...")
            try {
                const res = await api.post(`/professors/${id}/generate-email`, {
                    template: emailSettings.template,
                    tone: emailSettings.tone,
                    length: emailSettings.length,
                    custom_instructions: emailSettings.customInstructions
                })
                toast.success("Draft created!", { id: toastId })
                return res.data
            } catch (err: any) {
                toast.error("Failed to draft email", { id: toastId })
                throw err
            }
        },
        onSuccess: (data) => {
            setEmailDraft(data)
            queryClient.invalidateQueries({ queryKey: ['professor', id] })
        }
    })

    // Generate Card Mutation
    const generateCardMutation = useMutation({
        mutationFn: async () => {
            const toastId = toast.loading("Generating card...")
            try {
                await api.post(`/professors/${id}/generate-card`)
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

    // Status Mutation
    const statusMutation = useMutation({
        mutationFn: async (newStatus: string) => {
            return api.patch(`/professors/${id}/status`, { status: newStatus })
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['professor', id] })
            toast.success("Status updated")
        }
    })

    // Delete Mutation
    const deleteMutation = useMutation({
        mutationFn: async () => {
            await api.delete(`/professors/${id}`)
        },
        onSuccess: () => {
            toast.success("Professor deleted")
            router.push("/")
        },
        onError: (err: any) => {
            toast.error("Failed to delete professor: " + err.message)
        }
    })

    const handleDelete = () => {
        if (confirm("Are you sure you want to delete this professor? This action cannot be undone.")) {
            deleteMutation.mutate(undefined)
        }
    }

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
                <div className="flex justify-between items-center">
                    <Link href="/">
                        <Button variant="ghost" className="pl-0 gap-2 text-slate-500 hover:text-slate-900">
                            <ArrowLeft className="w-4 h-4" /> Back to Board
                        </Button>
                    </Link>
                    <Button variant="ghost" className="text-red-500 hover:text-red-700 hover:bg-red-50" onClick={handleDelete}>
                        <Trash2 className="w-4 h-4 mr-2" /> Delete Professor
                    </Button>
                </div>

                {/* Header */}
                <div className="bg-white rounded-xl p-6 border shadow-sm flex justify-between items-start">
                    <div className="flex gap-4 items-center">
                        {professor.avatar_url ? (
                            <img src={professor.avatar_url} alt={professor.name} className="w-16 h-16 rounded-full object-cover border border-slate-200" />
                        ) : (
                            <div className="w-16 h-16 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-bold text-xl">
                                {professor.name.split(" ").map((n: any) => n[0]).join("").substring(0, 2)}
                            </div>
                        )}
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className="text-2xl font-bold text-slate-900">{professor.name}</h1>
                                <div>
                                    <Select
                                        defaultValue={professor.target_role || "summer_intern"}
                                        onValueChange={(val) => {
                                            api.patch(`/professors/${id}`, { target_role: val })
                                                .then(() => {
                                                    toast.success("Role updated")
                                                    queryClient.invalidateQueries({ queryKey: ['professor', id] })
                                                })
                                        }}
                                    >
                                        <SelectTrigger className="h-6 w-auto text-xs px-2 py-0 border-transparent bg-slate-100 hover:bg-slate-200 text-slate-600 gap-1 rounded-full">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="summer_intern">Summer Intern</SelectItem>
                                            <SelectItem value="phd">PhD Student</SelectItem>
                                            <SelectItem value="postdoc">Postdoc</SelectItem>
                                            <SelectItem value="ra">Research Assistant</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                            <p className="text-slate-500">{professor.affiliation}</p>
                            <a href={professor.website_url} target="_blank" className="text-blue-600 text-sm hover:underline flex items-center gap-1 mt-1">
                                {professor.website_url} <ExternalLink className="w-3 h-3" />
                            </a>
                        </div>
                    </div>
                    <div className="flex gap-2 flex-wrap justify-end max-w-[50%]">
                        {["Draft", "Sent", "Replied", "Meeting", "Offer", "Rejection"].map(status => (
                            <Button
                                key={status}
                                variant={professor.pipeline_status?.status === status ? "default" : "outline"}
                                size="sm"
                                onClick={() => statusMutation.mutate(status)}
                                className={`text-xs ${professor.pipeline_status?.status === status ? (
                                    status === 'Offer' ? 'bg-green-600 hover:bg-green-700' :
                                        status === 'Rejection' ? 'bg-red-600 hover:bg-red-700' :
                                            status === 'Meeting' ? 'bg-purple-600 hover:bg-purple-700' :
                                                status === 'Replied' ? 'bg-yellow-600 hover:bg-yellow-700' :
                                                    status === 'Sent' ? 'bg-blue-600 hover:bg-blue-700' :
                                                        ''
                                ) : ''
                                    }`}
                            >
                                {status}
                            </Button>
                        ))}
                    </div>
                </div>

                {/* Content Tabs */}
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                    <TabsList className="bg-white p-1 border">
                        <TabsTrigger value="card" className="gap-2"><Sparkles className="w-4 h-4" /> Research Card</TabsTrigger>
                        <TabsTrigger value="email" className="gap-2"><Mail className="w-4 h-4" /> Email Draft</TabsTrigger>
                        <TabsTrigger value="source" className="gap-2"><FileText className="w-4 h-4" /> Source Text</TabsTrigger>
                    </TabsList>

                    <TabsContent value="card" className="mt-6 space-y-6">
                        {!latestCard ? (
                            <Card className="bg-slate-50 border-dashed">
                                <CardContent className="flex flex-col items-center justify-center py-12 space-y-4">
                                    <div className="p-4 bg-white rounded-full shadow-sm">
                                        <Sparkles className="w-8 h-8 text-slate-400" />
                                    </div>
                                    <div className="text-center">
                                        <h3 className="font-semibold text-slate-900">No Research Card Yet</h3>
                                        <p className="text-slate-500 text-sm max-w-sm mt-1">Generate a structured summary of this professor's research interests and recent work.</p>
                                    </div>
                                    <div className="flex flex-col gap-2 w-full">
                                        <div className="flex gap-2 w-full">
                                            <Button variant="outline" className="flex-1" onClick={() => ingestMutation.mutate(undefined)} disabled={ingestMutation.isPending}>
                                                {ingestMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                                                1. Fetch Website
                                            </Button>
                                            <Button className="flex-1" onClick={() => generateCardMutation.mutate(undefined)} disabled={generateCardMutation.isPending || visitorHasNoSource(professor)}>
                                                {generateCardMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                                                2. Generate Card
                                            </Button>
                                        </div>
                                        <div className="flex justify-center w-full">
                                            <Button variant="ghost" size="sm" onClick={() => generateCardMutation.mutate(undefined)}>
                                                <RefreshCw className="w-4 h-4 text-slate-400" />
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <Card className="md:col-span-2">
                                    <CardHeader>
                                        <CardTitle className="flex justify-between items-center">
                                            <span>Research Summary</span>
                                            <div className="flex gap-2">
                                                {cardData?.hiring_signals && cardData.hiring_signals.length > 0 && (
                                                    <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-bold flex items-center gap-1 border border-green-200 animate-pulse">
                                                        🚨 Hiring Detected
                                                    </span>
                                                )}
                                                <Button variant="ghost" size="sm" onClick={() => generateCardMutation.mutate(undefined)}>
                                                    <RefreshCw className="w-4 h-4 text-slate-400" />
                                                </Button>
                                            </div>
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-6">
                                        {cardData?.hiring_signals && cardData.hiring_signals.length > 0 && (
                                            <div className="bg-green-50 border border-green-100 p-4 rounded-lg">
                                                <h4 className="font-semibold text-green-800 text-sm mb-2">Potential Opening Detected</h4>
                                                <ul className="text-sm text-green-700 list-disc list-inside space-y-1">
                                                    {cardData.hiring_signals.map((signal: string, i: number) => (
                                                        <li key={i}>"{signal}"</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                        <div className="prose prose-slate max-w-none">
                                            <div className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                                                {latestCard.card_md}
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                                <Card className="h-fit">
                                    <CardHeader><CardTitle>Quick Facts</CardTitle></CardHeader>
                                    <CardContent className="space-y-4">
                                        <div>
                                            <Label className="text-xs text-slate-500 uppercase font-bold">Interests</Label>
                                            <div className="flex flex-wrap gap-2 mt-2">
                                                {cardData?.research_interests?.map((tag: string, i: number) => (
                                                    <span key={i} className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs font-medium border border-blue-100">{tag}</span>
                                                ))}
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        )}
                    </TabsContent>

                    <TabsContent value="email">
                        <Card>
                            <CardContent className="p-6">
                                <div className="text-center space-y-4">
                                    <h3 className="font-semibold text-lg">Generate Email Draft</h3>
                                    <p className="text-slate-500 text-sm">
                                        Use the extracted research info to draft a personalized email for
                                        <span className="font-medium text-slate-900"> {professor.target_role === 'phd' ? 'PhD Application' : 'Summer Internship'}</span>.
                                    </p>

                                    <div className="space-y-6 max-w-2xl mx-auto mt-6">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div className="space-y-2">
                                                <Label>Template</Label>
                                                <Select
                                                    value={emailSettings.template}
                                                    onValueChange={(val) => setEmailSettings({ ...emailSettings, template: val })}
                                                >
                                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="summer_intern">Summer Internship</SelectItem>
                                                        <SelectItem value="phd">PhD Application</SelectItem>
                                                        <SelectItem value="ra">Research Assistant</SelectItem>
                                                        <SelectItem value="postdoc">Postdoc</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                            <div className="space-y-2">
                                                <Label>Tone</Label>
                                                <Select
                                                    value={emailSettings.tone}
                                                    onValueChange={(val) => setEmailSettings({ ...emailSettings, tone: val })}
                                                >
                                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                                    <SelectContent>
                                                        <SelectItem value="formal">Formal</SelectItem>
                                                        <SelectItem value="enthusiastic">Enthusiastic</SelectItem>
                                                        <SelectItem value="direct">Direct</SelectItem>
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Length</Label>
                                            <Select
                                                value={emailSettings.length}
                                                onValueChange={(val) => setEmailSettings({ ...emailSettings, length: val })}
                                            >
                                                <SelectTrigger><SelectValue /></SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="short">Short</SelectItem>
                                                    <SelectItem value="medium">Medium</SelectItem>
                                                    <SelectItem value="long">Long</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div className="space-y-2">
                                            <Label>Custom Instructions (Optional)</Label>
                                            <textarea
                                                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                                placeholder="e.g. Mention that I read their paper on transformers..."
                                                value={emailSettings.customInstructions}
                                                onChange={(e) => setEmailSettings({ ...emailSettings, customInstructions: e.target.value })}
                                            />
                                        </div>

                                        <Button
                                            className="w-full"
                                            onClick={() => emailMutation.mutate()}
                                            disabled={emailMutation.isPending}
                                        >
                                            {emailMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                                            Generate Email Draft
                                        </Button>
                                    </div>

                                    {emailDraft && (
                                        <div className="mt-8 text-left border rounded-lg p-6 bg-white shadow-sm">
                                            <div className="flex justify-between items-center mb-4">
                                                <h4 className="font-bold text-slate-900">Generated Draft</h4>
                                                <Button variant="ghost" size="sm" onClick={() => navigator.clipboard.writeText(emailDraft.content_long)}>Copy to Clipboard</Button>
                                            </div>
                                            <div className="prose prose-sm max-w-none">
                                                <div className="mb-4 p-3 bg-slate-50 rounded text-xs font-mono">
                                                    Subject: {emailDraft.subject || `Inquiry regarding research opportunities - ${professor.name}`}
                                                </div>
                                                <div className="whitespace-pre-wrap">{emailDraft.content_long}</div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="source">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between py-4">
                                <CardTitle className="text-base">Source Content</CardTitle>
                                {professor.source_pages && professor.source_pages.length > 0 && (
                                    <div className="flex items-center gap-2 text-xs">
                                        <span className={`px-2 py-1 rounded-full font-medium border ${professor.source_pages[0].fetch_status === 'failed'
                                            ? 'bg-red-50 text-red-700 border-red-200'
                                            : 'bg-green-50 text-green-700 border-green-200'
                                            }`}>
                                            {professor.source_pages[0].fetch_status === 'failed' ? 'Failed' : 'Success'}
                                        </span>
                                        <span className="text-slate-500">
                                            {new Date(professor.source_pages[0].fetched_at).toLocaleString()}
                                        </span>
                                    </div>
                                )}
                            </CardHeader>
                            <CardContent className="p-0 border-t">
                                {professor.source_pages && professor.source_pages.length > 0 ? (
                                    <>
                                        {professor.source_pages[0].error_msg && (
                                            <div className="p-4 bg-red-50 text-red-700 text-sm border-b border-red-100">
                                                <strong>Error:</strong> {professor.source_pages[0].error_msg}
                                            </div>
                                        )}
                                        <div className="p-4 bg-slate-50">
                                            <div className="text-xs text-slate-500 mb-2 font-mono break-all">
                                                Source: <a href={professor.source_pages[0].source_url} target="_blank" className="text-blue-600 hover:underline">{professor.source_pages[0].source_url}</a>
                                            </div>
                                            <pre className="whitespace-pre-wrap text-xs text-slate-600 font-mono h-[500px] overflow-auto bg-white p-4 rounded border">
                                                {professor.source_pages[0].raw_text || "No text content extracted."}
                                            </pre>
                                        </div>
                                    </>
                                ) : (
                                    <div className="p-12 text-center text-slate-500">
                                        <p>No source content fetched yet.</p>
                                        <Button variant="outline" className="mt-4" onClick={() => ingestMutation.mutate(undefined)}>
                                            Fetch Website Now
                                        </Button>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>
        </div >
    )
}

function visitorHasNoSource(professor: any) {
    return !professor.source_pages || professor.source_pages.length === 0 || !professor.source_pages[0].raw_text
}
