import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import axios from "axios"
import { Plus, Search, ExternalLink, RefreshCw, Loader2, UserPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
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
import { API_URL } from "@/lib/config"

export function AddProfessorDialog() {
    const [open, setOpen] = useState(false)
    const [activeTab, setActiveTab] = useState("manual")
    const [newProf, setNewProf] = useState({ name: "", affiliation: "", website_url: "" })

    // Search State
    const [searchQuery, setSearchQuery] = useState("")
    const [searchResults, setSearchResults] = useState<any[]>([])
    const [isSearching, setIsSearching] = useState(false)

    const queryClient = useQueryClient()

    // Mutations
    const ingestMutation = useMutation({
        mutationFn: async (vars: { id: number, url: string }) => {
            return axios.post(`${API_URL}/ingest`, {
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
            return axios.post(`${API_URL}/professors/`, newProfessor)
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['professors'] })
            setOpen(false)
            setNewProf({ name: "", affiliation: "", website_url: "" })
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
            const res = await axios.get(`${API_URL}/search_professors?query=${encodeURIComponent(searchQuery)}`)
            setSearchResults(res.data)
        } catch (err) {
            toast.error("Search failed")
        } finally {
            setIsSearching(false)
        }
    }

    const handleSelectResult = (result: any) => {
        // Try to guess name/affiliation from title or snippet if possible
        // Result format: { title, link, snippet }
        // For now, we just fill the URL and Title into Name, user can edit.
        setNewProf({
            name: result.title.split(" - ")[0] || result.title, // naive guess
            affiliation: "", // user needs to fill
            website_url: result.link
        })
        setActiveTab("manual")
        toast.info("Details auto-filled. Please review and save.")
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
                                <Card key={i} className="cursor-pointer hover:bg-slate-100 transition-colors" onClick={() => handleSelectResult(result)}>
                                    <CardContent className="p-3">
                                        <h4 className="font-semibold text-sm text-blue-700 line-clamp-1">{result.title}</h4>
                                        <p className="text-xs text-slate-500 line-clamp-1 mb-1">{result.link}</p>
                                        <p className="text-xs text-slate-600 line-clamp-2">{result.snippet}</p>
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
