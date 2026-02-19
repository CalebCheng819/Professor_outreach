import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import api from "@/lib/api"
import { Plus, Search, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { toast } from "sonner"
import { Card, CardContent } from "@/components/ui/card"

export function AddProfessorDialog() {
    const [open, setOpen] = useState(false)
    const [activeTab, setActiveTab] = useState("manual")
    const [newProf, setNewProf] = useState({ name: "", affiliation: "", website_url: "", target_role: "summer_intern", avatar_url: "" })

    // Search State
    const [searchQuery, setSearchQuery] = useState("")
    const [searchResults, setSearchResults] = useState<any[]>([])
    const [isSearching, setIsSearching] = useState(false)

    const queryClient = useQueryClient()

    // Mutations
    const ingestMutation = useMutation({
        mutationFn: async (vars: { id: number, url: string }) => {
            return api.post("/ingest", {
                professor_id: vars.id,
                url: vars.url
            })
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['professors'] })
            toast.success("Website fetched successfully!")
        },
        onError: (err: any) => {
            toast.error("Failed to fetch website: " + err.message)
        }
    })

    const addMutation = useMutation({
        mutationFn: async (newProfessor: any) => {
            return api.post("/professors/", newProfessor)
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['professors'] })
            setOpen(false)
            setNewProf({ name: "", affiliation: "", website_url: "", target_role: "summer_intern", avatar_url: "" })
            toast.success("Professor added!")

            // Auto-Ingest if URL is present
            if (data.data.website_url) {
                toast.info("Auto-fetching website...", { duration: 2000 })
                ingestMutation.mutate({ id: data.data.id, url: data.data.website_url })
            }
        },
        onError: (err) => {
            toast.error("Failed to add professor")
        }
    })

    const handleSearch = async () => {
        if (!searchQuery) return
        setIsSearching(true)
        setSearchResults([])
        try {
            const res = await api.get(`/search_professors?query=${encodeURIComponent(searchQuery)}`)
            setSearchResults(res.data)
        } catch (err) {
            toast.error("Search failed")
        } finally {
            setIsSearching(false)
        }
    }

    // State for avatar scanning
    const [isScanningAvatar, setIsScanningAvatar] = useState(false)

    const extractAvatar = async (website_url: string, name: string) => {
        setIsScanningAvatar(true)
        try {
            const res = await api.post("/extract_avatar", { website_url, name })
            if (res.data?.avatar_url) {
                setNewProf(prev => ({ ...prev, avatar_url: res.data.avatar_url }))
                toast.success("📸 Found professor photo!")
            } else {
                // toast.info("No profile photo found on website.")
            }
        } catch (e) {
            console.error("Avatar extraction failed:", e)
        } finally {
            setIsScanningAvatar(false)
        }
    }

    // State for parsing selection
    const [parsingId, setParsingId] = useState<string | null>(null)

    const handleSelectResult = async (result: any) => {
        setParsingId(result.link) // or result.title if link is not unique enough, but link is better

        // Start with rule-based name from search as fallback
        let name = result.name || result.title;
        let affiliation = result.affiliation || "";
        let website_url = result.link;

        try {
            // 1. Trigger AI Text Parsing (Wait for this)
            const parseRes = await api.post("/parse_search_result", {
                query: searchQuery,
                title: result.title,
                snippet: result.snippet,
                link: result.link
            })

            if (parseRes.data && parseRes.data.confidence > 0.5) {
                name = parseRes.data.name || name
                affiliation = parseRes.data.affiliation || affiliation
                toast.success(`✅ Analyzed: ${name}`)
            }
        } catch (err) {
            console.warn("AI text parse failed, using fallback:", err)
        }

        // 2. Set State
        setNewProf(prev => ({
            ...prev,
            name: name,
            affiliation: affiliation,
            website_url: website_url,
            target_role: "summer_intern",
            avatar_url: ""
        }))

        // 3. Switch Tab
        setActiveTab("manual")
        setParsingId(null)

        // 4. Trigger Avatar Extraction (Background)
        // We do this AFTER switching so user sees the "Scanning..." indicator on the form
        extractAvatar(website_url, name);
    }

    const handleAdd = () => {
        if (!newProf.name) {
            toast.error("Name is required")
            return
        }
        addMutation.mutate(newProf)
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button><Plus className="mr-2 h-4 w-4" /> Add Professor</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px] bg-white">
                <DialogHeader>
                    <DialogTitle>Add New Professor</DialogTitle>
                    <DialogDescription>
                        Search online or enter details manually.
                    </DialogDescription>
                </DialogHeader>

                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="manual">Manual Entry</TabsTrigger>
                        <TabsTrigger value="search">Search Web</TabsTrigger>
                    </TabsList>

                    <TabsContent value="manual" className="space-y-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="name" className="text-right">Name</Label>
                            <Input id="name" value={newProf.name} onChange={e => setNewProf({ ...newProf, name: e.target.value })} className="col-span-3" placeholder="e.g. Geoffrey Hinton" />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="aff" className="text-right">Affiliation</Label>
                            <Input id="aff" value={newProf.affiliation} onChange={e => setNewProf({ ...newProf, affiliation: e.target.value })} className="col-span-3" placeholder="e.g. Univ of Toronto" />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="url" className="text-right">Website</Label>
                            <Input id="url" value={newProf.website_url} onChange={e => setNewProf({ ...newProf, website_url: e.target.value })} className="col-span-3" placeholder="https://..." />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="avatar" className="text-right">Avatar URL</Label>
                            <div className="col-span-3 flex gap-2 items-center">
                                <Input
                                    id="avatar"
                                    value={newProf.avatar_url || ""}
                                    onChange={e => setNewProf({ ...newProf, avatar_url: e.target.value })}
                                    placeholder="https://..."
                                    className="flex-1"
                                />
                                {isScanningAvatar && (
                                    <div className="flex items-center text-xs text-amber-600 animate-pulse whitespace-nowrap">
                                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                                        Scanning...
                                    </div>
                                )}
                                {newProf.avatar_url && !isScanningAvatar && (
                                    <img src={newProf.avatar_url} alt="Preview" className="w-8 h-8 rounded-full border object-cover" />
                                )}
                            </div>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="role" className="text-right">Target Role</Label>
                            <Select onValueChange={(val) => setNewProf({ ...newProf, target_role: val })} defaultValue={newProf.target_role}>
                                <SelectTrigger className="col-span-3">
                                    <SelectValue placeholder="Select role" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="summer_intern">Summer Intern</SelectItem>
                                    <SelectItem value="phd">PhD Student</SelectItem>
                                    <SelectItem value="postdoc">Postdoc</SelectItem>
                                    <SelectItem value="ra">Research Assistant</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <DialogFooter>
                            <Button onClick={handleAdd} disabled={addMutation.isPending}>
                                {addMutation.isPending ? "Saving..." : "Save Professor"}
                            </Button>
                        </DialogFooter>
                    </TabsContent>

                    <TabsContent value="search" className="space-y-4 py-4">
                        <div className="flex gap-2">
                            <Input
                                placeholder="Search professor (e.g. 'Andrew Ng Stanford')"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                            />
                            <Button onClick={handleSearch} disabled={isSearching}>
                                {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                            </Button>
                        </div>

                        <div className="h-[300px] overflow-y-auto space-y-2 border rounded-md p-2 bg-slate-50">
                            {searchResults.length === 0 && !isSearching && (
                                <div className="text-center text-slate-400 text-sm mt-10">
                                    No results. Try a different query.
                                </div>
                            )}
                            {searchResults.map((result, i) => (
                                <Card key={i} className={`cursor-pointer transition-colors ${parsingId === result.link ? 'bg-blue-50 border-blue-200' : 'hover:bg-slate-100'}`} onClick={() => !parsingId && handleSelectResult(result)}>
                                    <CardContent className="p-3 flex items-start justify-between">
                                        <div>
                                            <h4 className="font-semibold text-sm text-blue-700 line-clamp-1">{result.title}</h4>
                                            <p className="text-xs text-slate-500 line-clamp-1 mb-1">{result.link}</p>
                                            <p className="text-xs text-slate-600 line-clamp-2">{result.snippet}</p>
                                        </div>
                                        {parsingId === result.link && (
                                            <Loader2 className="w-4 h-4 text-blue-500 animate-spin shrink-0 ml-2" />
                                        )}
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    )
}
