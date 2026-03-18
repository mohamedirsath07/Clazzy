/**
 * OutfitHistory - Display saved outfits from history
 */

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { History, Trash2, X, Clock, Sparkles } from "lucide-react";
import { getOutfitHistory, deleteOutfitFromHistory, type SavedOutfit } from "@/lib/outfitHistory";

interface OutfitHistoryProps {
    onClose: () => void;
}

export function OutfitHistory({ onClose }: OutfitHistoryProps) {
    const [outfits, setOutfits] = useState<SavedOutfit[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        setIsLoading(true);
        try {
            const history = await getOutfitHistory();
            setOutfits(history);
        } catch (error) {
            console.error('Failed to load history:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (outfitId: string) => {
        try {
            await deleteOutfitFromHistory(outfitId);
            setOutfits(prev => prev.filter(o => o.id !== outfitId));
        } catch (error) {
            console.error('Failed to delete outfit:', error);
        }
    };

    const formatDate = (timestamp: number) => {
        return new Date(timestamp).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <Card className="max-w-6xl w-full p-6 max-h-[90vh] overflow-auto bg-gray-900 border-gray-800">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="bg-purple-600 p-2 rounded-lg">
                            <History className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white">Saved Collection</h2>
                            <p className="text-sm text-gray-400">{outfits.length} saved outfits</p>
                        </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={onClose}>
                        <X className="h-5 w-5" />
                    </Button>
                </div>

                {isLoading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
                        <p className="text-gray-400">Loading your outfit history...</p>
                    </div>
                ) : outfits.length === 0 ? (
                    <div className="text-center py-12">
                        <History className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                        <h3 className="text-xl font-semibold mb-2 text-white">No saved outfits yet</h3>
                        <p className="text-gray-400 mb-4">
                            Generate outfit recommendations and click "Add to Saved Collection" to save them here.
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {outfits.map((outfit) => (
                            <Card key={outfit.id} className="overflow-hidden bg-gray-800 border-gray-700 hover:border-purple-500/50 transition-all">
                                <CardContent className="p-0">
                                    {/* Outfit Images */}
                                    <div className="grid grid-cols-2 gap-1 p-2 bg-gray-700/30">
                                        <div className="relative aspect-square overflow-hidden rounded-lg">
                                            <img
                                                src={outfit.topUrl}
                                                alt="Top"
                                                className="h-full w-full object-cover"
                                                onError={(e) => {
                                                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23333" width="200" height="200"/%3E%3Ctext fill="%23666" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                                                }}
                                            />
                                            <div className="absolute bottom-1 left-1 rounded bg-blue-600/80 px-2 py-0.5 text-xs text-white font-medium">
                                                TOP
                                            </div>
                                        </div>
                                        <div className="relative aspect-square overflow-hidden rounded-lg">
                                            <img
                                                src={outfit.bottomUrl}
                                                alt="Bottom"
                                                className="h-full w-full object-cover"
                                                onError={(e) => {
                                                    (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23333" width="200" height="200"/%3E%3Ctext fill="%23666" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3ENo Image%3C/text%3E%3C/svg%3E';
                                                }}
                                            />
                                            <div className="absolute bottom-1 left-1 rounded bg-amber-600/80 px-2 py-0.5 text-xs text-white font-medium">
                                                BOTTOM
                                            </div>
                                        </div>
                                    </div>

                                    {/* Details */}
                                    <div className="p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <Badge variant="outline" className="capitalize text-purple-400 border-purple-400/50">
                                                {outfit.occasion}
                                            </Badge>
                                            <div className="flex items-center gap-1 text-green-400">
                                                <Sparkles className="h-3 w-3" />
                                                <span className="text-xs font-medium">{Math.round(outfit.score * 100)}%</span>
                                            </div>
                                        </div>

                                        <div className="flex items-center justify-between text-xs text-gray-500">
                                            <div className="flex items-center gap-1">
                                                <Clock className="h-3 w-3" />
                                                {formatDate(outfit.savedAt)}
                                            </div>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 px-2 text-red-400 hover:text-red-300 hover:bg-red-400/10"
                                                onClick={() => handleDelete(outfit.id)}
                                            >
                                                <Trash2 className="h-3 w-3 mr-1" />
                                                Remove
                                            </Button>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}

                <div className="mt-6 flex justify-end">
                    <Button onClick={onClose} className="bg-purple-600 hover:bg-purple-700">
                        Close
                    </Button>
                </div>
            </Card>
        </div>
    );
}
