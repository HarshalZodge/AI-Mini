import React, { useState, useEffect, useMemo } from 'react';
import { 
  Users, 
  MapPin, 
  ThumbsUp, 
  CheckCircle2, 
  Clock, 
  Building2, 
  Filter, 
  Sparkles,
  FileText,
  Search,
  ExternalLink
} from 'lucide-react';
import { motion } from 'framer-motion';
import { fetchComplaints, upvoteComplaint } from '../lib/api';
import FormalLetterModal from '../components/FormalLetterModal';

const AHILYANAGAR_AREAS = [
  "All Ahilyanagar",
  "Savedi",
  "Kedgaon",
  "Bhingar",
  "Pipeline Road",
  "Tarakpur",
  "Delhi Gate",
  "Maliwada",
  "Nagapur MIDC",
  "Kotla",
  "Burudgaon Road",
  "Bolhegaon",
  "DSP Chowk",
  "Gulshanabad"
];

export default function CommunityFeedPage({ onNavigateTrack }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArea, setSelectedArea] = useState("All Ahilyanagar");
  const [filterType, setFilterType] = useState("all"); // 'all', 'trending', 'resolved'
  const [searchQuery, setSearchQuery] = useState("");
  const [upvotedIds, setUpvotedIds] = useState({});
  const [letterModalOpen, setLetterModalOpen] = useState(false);
  const [letterConfig, setLetterConfig] = useState({ text: '', title: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchComplaints({ sortBy: 'upvotes' });
      setComplaints(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpvote = async (trackingId) => {
    if (upvotedIds[trackingId]) return;
    try {
      const res = await upvoteComplaint(trackingId);
      setUpvotedIds(prev => ({ ...prev, [trackingId]: true }));
      setComplaints(prev => prev.map(c => c.tracking_id === trackingId ? { ...c, upvotes: res.upvotes } : c));
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = useMemo(() => {
    return complaints.filter(c => {
      if (selectedArea !== "All Ahilyanagar") {
        const locLower = (c.location || "").toLowerCase();
        if (!locLower.includes(selectedArea.toLowerCase())) return false;
      }
      if (filterType === "resolved" && c.status !== "Resolved") return false;
      if (filterType === "trending" && (c.upvotes < 25 || c.status === "Resolved")) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          c.title?.toLowerCase().includes(q) ||
          c.location?.toLowerCase().includes(q) ||
          c.category?.toLowerCase().includes(q) ||
          c.tracking_id?.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [complaints, selectedArea, filterType, searchQuery]);

  return (
    <div className="max-w-[1000px] mx-auto px-4 sm:px-6 py-8 min-h-[calc(100vh-4rem)] space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#ECECE8] dark:border-[#27272A]">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] text-xs font-semibold mb-2">
            <Users className="w-3.5 h-3.5" />
            <span>Citizen Community Wall</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#111111] dark:text-[#F4F4F5] tracking-tight">
            Neighborhood Pulse
          </h1>
          <p className="text-xs sm:text-sm text-[#6B7280] dark:text-[#9CA3AF] mt-1">
            See what civic issues are active around your locality in Ahilyanagar. Endorse complaints with your vote to raise their municipal priority.
          </p>
        </div>

        {/* Tab Filters */}
        <div className="flex items-center gap-1 self-start sm:self-auto bg-[#FFFFFF] dark:bg-[#17171A] p-1 rounded-xl border border-[#ECECE8] dark:border-[#27272A] shadow-xs text-xs">
          <button
            onClick={() => setFilterType("all")}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
              filterType === "all"
                ? "bg-[#5B5BD6] text-white shadow-xs"
                : "text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]"
            }`}
          >
            All Reports ({complaints.length})
          </button>
          <button
            onClick={() => setFilterType("trending")}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
              filterType === "trending"
                ? "bg-[#5B5BD6] text-white shadow-xs"
                : "text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]"
            }`}
          >
            🔥 High Impact
          </button>
          <button
            onClick={() => setFilterType("resolved")}
            className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
              filterType === "resolved"
                ? "bg-[#5B5BD6] text-white shadow-xs"
                : "text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]"
            }`}
          >
            ✅ Resolved
          </button>
        </div>
      </div>

      {/* Filter Chips by Locality */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar text-xs">
        <span className="text-[#6B7280] dark:text-[#9CA3AF] shrink-0 font-medium text-[11px]">Area:</span>
        {AHILYANAGAR_AREAS.map((area) => (
          <button
            key={area}
            onClick={() => setSelectedArea(area)}
            className={`shrink-0 px-3 py-1.5 rounded-xl border text-xs font-medium transition-all ${
              selectedArea === area
                ? 'bg-[#5B5BD6] text-white border-[#5B5BD6]'
                : 'bg-[#FFFFFF] dark:bg-[#17171A] text-[#4B5563] dark:text-[#D1D5DB] border-[#ECECE8] dark:border-[#27272A] hover:border-[#5B5BD6]/40'
            }`}
          >
            {area}
          </button>
        ))}
      </div>

      {/* Search Input */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-[#9CA3AF] absolute left-3.5 top-3" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search neighborhood, street, or issue..."
          className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] text-[#111111] dark:text-[#F4F4F5] focus:outline-hidden focus:ring-1 focus:ring-[#5B5BD6]"
        />
      </div>

      {/* Complaints Grid */}
      {loading ? (
        <div className="py-12 text-center">
          <div className="w-8 h-8 rounded-full border-2 border-[#5B5BD6] border-t-transparent animate-spin mx-auto"></div>
          <p className="mt-2 text-xs text-[#6B7280]">Loading neighborhood reports...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-12 text-center p-8 bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A]">
          <p className="text-sm font-medium text-[#6B7280] dark:text-[#9CA3AF]">
            No reports found for "{selectedArea}" matching the current filter.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((c) => {
            const isResolved = c.status === "Resolved";
            const priorityColor = c.priority >= 4 ? 'bg-[#E5484D]' : c.priority === 3 ? 'bg-[#F2A33A]' : 'bg-[#34A874]';
            const isUpvoted = upvotedIds[c.tracking_id];

            return (
              <motion.div
                key={c.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] p-5 shadow-xs flex flex-col justify-between hover:shadow-sm transition-all"
              >
                <div>
                  {/* Top Bar */}
                  <div className="flex items-center justify-between gap-2 pb-2.5 border-b border-[#ECECE8] dark:border-[#27272A]">
                    <span className="font-mono text-xs font-bold text-[#5B5BD6] dark:text-[#8383FF] bg-[#EEF0FF] dark:bg-[#1C1C30] px-2 py-0.5 rounded-md">
                      {c.tracking_id}
                    </span>

                    <div className="flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${priorityColor}`} />
                      <span className="text-[11px] font-medium text-[#6B7280] dark:text-[#9CA3AF]">
                        P{c.priority}
                      </span>
                      <span className={`ml-1 text-[11px] font-medium px-2 py-0.5 rounded-full ${
                        isResolved
                          ? 'bg-[#EBF8F2] text-[#34A874] dark:bg-[#11271D]'
                          : 'bg-[#FAFAF8] dark:bg-[#1F1F24] text-[#6B7280] dark:text-[#A1A1AA] border border-[#ECECE8] dark:border-[#27272A]'
                      }`}>
                        {c.status}
                      </span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <div className="pt-3">
                    <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5] leading-snug line-clamp-1">
                      {c.title}
                    </h3>
                    <p className="mt-1 text-xs text-[#6B7280] dark:text-[#9CA3AF] line-clamp-2 leading-relaxed">
                      {c.description}
                    </p>
                  </div>

                  {/* Meta */}
                  <div className="mt-3 space-y-1 text-xs text-[#4B5563] dark:text-[#9CA3AF]">
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-[#5B5BD6] shrink-0" />
                      <span className="truncate">{c.location}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-[#9CA3AF] shrink-0" />
                      <span className="truncate">{c.department}</span>
                    </div>
                  </div>
                </div>

                {/* Bottom Actions */}
                <div className="mt-4 pt-3 border-t border-[#ECECE8] dark:border-[#27272A] flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleUpvote(c.tracking_id)}
                    disabled={isUpvoted}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isUpvoted
                        ? 'bg-[#34A874] text-white'
                        : 'border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#EEF0FF] hover:text-[#5B5BD6] text-[#374151] dark:text-[#D1D5DB]'
                    }`}
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                    <span>{isUpvoted ? `Endorsed (${c.upvotes})` : `I Face This Too (${c.upvotes})`}</span>
                  </button>

                  <div className="flex items-center gap-1.5">
                    {c.formal_letter && (
                      <button
                        onClick={() => {
                          setLetterConfig({
                            text: c.formal_letter,
                            title: `Statutory Petition (${c.tracking_id})`
                          });
                          setLetterModalOpen(true);
                        }}
                        className="p-1.5 rounded-lg text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#5B5BD6] hover:bg-[#F4F4F2] dark:hover:bg-[#202024]"
                        title="View formal letter"
                      >
                        <FileText className="w-4 h-4" />
                      </button>
                    )}

                    <button
                      onClick={() => onNavigateTrack(c.tracking_id)}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-[#5B5BD6] dark:text-[#8383FF] hover:bg-[#EEF0FF] dark:hover:bg-[#1C1C30]"
                    >
                      <span>Track</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Formal Letter Modal */}
      <FormalLetterModal
        isOpen={letterModalOpen}
        onClose={() => setLetterModalOpen(false)}
        letterText={letterConfig.text}
        title={letterConfig.title}
      />
    </div>
  );
}
