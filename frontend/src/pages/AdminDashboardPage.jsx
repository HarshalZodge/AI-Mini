import React, { useState, useEffect, useMemo } from 'react';
import { 
  Building2, 
  MapPin, 
  Clock, 
  ShieldAlert, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  Filter, 
  ChevronDown, 
  ArrowUpDown,
  ThumbsUp,
  FileText,
  RotateCcw,
  Layers,
  TrendingUp,
  PieChart as PieIcon,
  BarChart2
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid 
} from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import FormalLetterModal from '../components/FormalLetterModal';
import { fetchComplaints, updateComplaintStatus, upvoteComplaint, fetchInsights, reseedDatabase } from '../lib/api';

const CATEGORIES = [
  "All",
  "Roads & Potholes",
  "Water Supply",
  "Sanitation & Garbage",
  "Electricity & Streetlights",
  "Drainage & Sewage",
  "Public Safety",
  "Parks & Public Spaces",
  "Noise & Pollution"
];

const STATUSES = ["All", "Submitted", "Assigned", "In Progress", "Resolved"];
const PRIORITIES = ["All", 5, 4, 3, 2, 1];

const COLORS = ['#5B5BD6', '#34A874', '#F2A33A', '#E5484D', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16'];

// Custom HTML DivIcon for Leaflet markers colored by priority
const createPriorityMarkerIcon = (priority) => {
  const color = priority >= 4 ? '#E5484D' : priority === 3 ? '#F2A33A' : '#34A874';
  const size = priority >= 4 ? 18 : priority === 3 ? 15 : 13;
  return L.divIcon({
    className: 'custom-map-pin',
    html: `
      <div style="
        width: ${size}px;
        height: ${size}px;
        background-color: ${color};
        border-radius: 50%;
        border: 2.5px solid #ffffff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.35);
        display: flex;
        align-items: center;
        justify-content: center;
      "></div>
    `,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    popupAnchor: [0, -size / 2],
  });
};

export default function AdminDashboardPage({ onNavigateTrack }) {
  const [complaints, setComplaints] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedStatus, setSelectedStatus] = useState("All");
  const [selectedPriority, setSelectedPriority] = useState("All");
  const [sortBy, setSortBy] = useState("created_at");
  const [searchQuery, setSearchQuery] = useState("");
  const [letterModalOpen, setLetterModalOpen] = useState(false);
  const [letterText, setLetterText] = useState("");
  const [letterTitle, setLetterTitle] = useState("");
  const [reseedLoading, setReseedLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [list, insightData] = await Promise.all([
        fetchComplaints(),
        fetchInsights()
      ]);
      setComplaints(list);
      setInsights(insightData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStatusChange = async (trackingId, newStatus) => {
    try {
      const updated = await updateComplaintStatus(trackingId, newStatus);
      setComplaints(prev => prev.map(c => c.tracking_id === trackingId ? updated : c));
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpvote = async (trackingId) => {
    try {
      const res = await upvoteComplaint(trackingId);
      setComplaints(prev => prev.map(c => c.tracking_id === trackingId ? { ...c, upvotes: res.upvotes } : c));
    } catch (err) {
      console.error(err);
    }
  };

  const handleReseed = async () => {
    setReseedLoading(true);
    try {
      await reseedDatabase();
      await loadData();
    } catch (err) {
      console.error(err);
    } finally {
      setReseedLoading(false);
    }
  };

  // Filtered complaints for table and map
  const filteredComplaints = useMemo(() => {
    return complaints.filter(c => {
      if (selectedCategory !== "All" && c.category !== selectedCategory) return false;
      if (selectedStatus !== "All" && c.status !== selectedStatus) return false;
      if (selectedPriority !== "All" && c.priority !== Number(selectedPriority)) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          c.title?.toLowerCase().includes(q) ||
          c.location?.toLowerCase().includes(q) ||
          c.tracking_id?.toLowerCase().includes(q) ||
          c.category?.toLowerCase().includes(q)
        );
      }
      return true;
    }).sort((a, b) => {
      if (sortBy === "upvotes") return b.upvotes - a.upvotes;
      if (sortBy === "priority") return b.priority - a.priority;
      return new Date(b.created_at) - new Date(a.created_at);
    });
  }, [complaints, selectedCategory, selectedStatus, selectedPriority, searchQuery, sortBy]);

  // Summary Metrics
  const stats = useMemo(() => {
    const total = complaints.length;
    const resolved = complaints.filter(c => c.status === "Resolved").length;
    const open = total - resolved;
    const highPriority = complaints.filter(c => c.priority >= 4).length;
    return { total, open, resolved, highPriority, avgResolutionDays: 3.4 };
  }, [complaints]);

  // Category Distribution for Chart
  const categoryChartData = useMemo(() => {
    const counts = {};
    complaints.forEach(c => {
      counts[c.category] = (counts[c.category] || 0) + 1;
    });
    return Object.keys(counts).map(key => ({
      name: key,
      value: counts[key]
    })).sort((a, b) => b.value - a.value);
  }, [complaints]);

  // Priority Breakdown for Chart
  const priorityChartData = useMemo(() => {
    const counts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    complaints.forEach(c => {
      counts[c.priority] = (counts[c.priority] || 0) + 1;
    });
    return [
      { priority: 'Level 1', count: counts[1] },
      { priority: 'Level 2', count: counts[2] },
      { priority: 'Level 3', count: counts[3] },
      { priority: 'Level 4', count: counts[4] },
      { priority: 'Level 5 (Critical)', count: counts[5] },
    ];
  }, [complaints]);

  return (
    <div className="max-w-[1100px] mx-auto px-4 sm:px-6 py-8 min-h-[calc(100vh-4rem)] space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#ECECE8] dark:border-[#27272A]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#111111] dark:text-[#F4F4F5] tracking-tight">
            Municipal Redressal Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-[#6B7280] dark:text-[#9CA3AF] mt-1">
            Real-time grievance telemetry, spatial clustering, and Gemini civic intelligence.
          </p>
        </div>

        <button
          onClick={handleReseed}
          disabled={reseedLoading}
          className="flex items-center gap-1.5 self-start sm:self-auto px-3.5 py-2 rounded-xl text-xs font-medium border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] text-[#4B5563] dark:text-[#D1D5DB] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] transition-colors"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${reseedLoading ? 'animate-spin' : ''}`} />
          <span>Reset Sample Complaints</span>
        </button>
      </div>

      {/* 4 Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
          <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">Total Complaints</span>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#111111] dark:text-[#F4F4F5] mt-1.5 tracking-tight">
            {stats.total}
          </p>
          <span className="text-[11px] text-[#34A874] mt-1 inline-block">100% AI Structured</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
          <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">Open Cases</span>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#F2A33A] mt-1.5 tracking-tight">
            {stats.open}
          </p>
          <span className="text-[11px] text-[#6B7280] dark:text-[#9CA3AF] mt-1 inline-block">In Field Remediation</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
          <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">Resolved Cases</span>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#34A874] mt-1.5 tracking-tight">
            {stats.resolved}
          </p>
          <span className="text-[11px] text-[#34A874] mt-1 inline-block">Verified by Supervisors</span>
        </div>

        <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
          <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">Avg. Resolution SLA</span>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#5B5BD6] dark:text-[#8383FF] mt-1.5 tracking-tight">
            {stats.avgResolutionDays} <span className="text-base font-normal">days</span>
          </p>
          <span className="text-[11px] text-[#5B5BD6] dark:text-[#8383FF] mt-1 inline-block">Citizen Charter Standard</span>
        </div>
      </div>

      {/* AI Weekly Insight Card */}
      {insights && (
        <div className="p-5 rounded-2xl bg-[#EEF0FF]/60 dark:bg-[#1A1A2E]/50 border border-[#5B5BD6]/25 shadow-xs">
          <div className="flex items-center gap-2 pb-3 border-b border-[#5B5BD6]/20">
            <div className="w-6 h-6 rounded-lg bg-[#5B5BD6] text-white flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <h2 className="font-semibold text-sm text-[#5B5BD6] dark:text-[#8383FF]">
              Gemini AI Municipal Intelligence Brief
            </h2>
            <span className="ml-auto text-[11px] text-[#6B7280] dark:text-[#9CA3AF] font-mono">
              {insights.generated_at}
            </span>
          </div>

          <p className="mt-3 text-xs sm:text-sm text-[#374151] dark:text-[#D1D5DB] leading-relaxed">
            {insights.summary}
          </p>

          <div className="mt-4 pt-3 border-t border-[#5B5BD6]/20 grid grid-cols-1 md:grid-cols-3 gap-3">
            {insights.recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-white/70 dark:bg-[#17171A]/70 border border-[#5B5BD6]/15 text-xs text-[#1F2937] dark:text-[#E5E7EB] space-y-1"
              >
                <span className="font-semibold text-[#5B5BD6] dark:text-[#8383FF] text-[11px] block">
                  Action Recommendation {idx + 1}
                </span>
                <p className="leading-snug">{rec}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Visual Analytics Row: Category Donut + Priority Bar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown Donut */}
        <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
          <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5] flex items-center gap-2 mb-4">
            <PieIcon className="w-4 h-4 text-[#5B5BD6]" />
            Grievances by Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {categoryChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#17171A', 
                    borderRadius: '8px', 
                    border: '1px solid #27272A',
                    fontSize: '12px',
                    color: '#fff'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Legend */}
          <div className="mt-2 flex flex-wrap gap-2 justify-center text-[11px]">
            {categoryChartData.slice(0, 5).map((entry, index) => (
              <div key={index} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }}></span>
                <span className="text-[#6B7280] dark:text-[#9CA3AF]">{entry.name} ({entry.value})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Distribution Bar */}
        <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
          <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5] flex items-center gap-2 mb-4">
            <BarChart2 className="w-4 h-4 text-[#5B5BD6]" />
            Priority Severity Spectrum (1-5)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priorityChartData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                <XAxis dataKey="priority" stroke="#888888" fontSize={11} tickLine={false} />
                <YAxis stroke="#888888" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ 
                    backgroundColor: '#17171A', 
                    borderRadius: '8px', 
                    border: '1px solid #27272A',
                    fontSize: '12px',
                    color: '#fff'
                  }} 
                />
                <Bar dataKey="count" fill="#5B5BD6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-center text-[#6B7280] dark:text-[#9CA3AF] mt-2">
            Priority evaluated automatically based on proximity to schools, hospitals, and life hazards.
          </p>
        </div>
      </div>

      {/* Spatial Map of Ahilyanagar Grievances */}
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5] flex items-center gap-2">
              <MapPin className="w-4 h-4 text-[#5B5BD6]" />
              Ahilyanagar City Civic Heatmap & Geo-Pins
            </h3>
            <p className="text-xs text-[#6B7280] dark:text-[#9CA3AF] mt-0.5">
              Interactive OpenStreetMap markers colored by priority level. Click any pin to inspect and endorse.
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#E5484D]"></span>
              <span className="text-[#6B7280] dark:text-[#9CA3AF]">Critical (P4-5)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#F2A33A]"></span>
              <span className="text-[#6B7280] dark:text-[#9CA3AF]">Medium (P3)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#34A874]"></span>
              <span className="text-[#6B7280] dark:text-[#9CA3AF]">Standard (P1-2)</span>
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="h-[360px] w-full rounded-xl overflow-hidden border border-[#ECECE8] dark:border-[#27272A]">
          <MapContainer
            center={[19.0952, 74.7496]}
            zoom={13}
            scrollWheelZoom={false}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {filteredComplaints.filter(c => c.latitude && c.longitude).map((c) => (
              <Marker
                key={c.id}
                position={[c.latitude, c.longitude]}
                icon={createPriorityMarkerIcon(c.priority)}
              >
                <Popup>
                  <div className="p-1 space-y-1.5 text-xs max-w-[220px]">
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-mono font-bold text-[#5B5BD6]">{c.tracking_id}</span>
                      <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-gray-100 text-gray-800">
                        P{c.priority}
                      </span>
                    </div>
                    <p className="font-semibold text-gray-900 leading-snug">{c.title}</p>
                    <p className="text-gray-600 text-[11px]">{c.location}</p>
                    <div className="pt-1.5 border-t border-gray-200 flex items-center justify-between">
                      <span className="text-[10px] text-gray-500">{c.status}</span>
                      <button
                        onClick={() => handleUpvote(c.tracking_id)}
                        className="text-[11px] text-[#5B5BD6] font-medium hover:underline flex items-center gap-1"
                      >
                        <ThumbsUp className="w-3 h-3" />
                        <span>Upvote ({c.upvotes})</span>
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
      </div>

      {/* Filterable / Sortable Complaints Table */}
      <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#ECECE8] dark:border-[#27272A]">
          <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5] flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#5B5BD6]" />
            Grievance Registry ({filteredComplaints.length})
          </h3>

          {/* Search box */}
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by area, ID, or title..."
            className="px-3 py-1.5 text-xs rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5] focus:outline-hidden focus:ring-1 focus:ring-[#5B5BD6]"
          />
        </div>

        {/* Filter Chips Bar */}
        <div className="flex flex-wrap items-center gap-2.5 text-xs">
          {/* Category Dropdown */}
          <div className="flex items-center gap-1">
            <span className="text-[#6B7280] dark:text-[#9CA3AF] text-[11px]">Category:</span>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="py-1 px-2.5 rounded-lg border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5] text-xs"
            >
              {CATEGORIES.map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>

          {/* Status Dropdown */}
          <div className="flex items-center gap-1">
            <span className="text-[#6B7280] dark:text-[#9CA3AF] text-[11px]">Status:</span>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="py-1 px-2.5 rounded-lg border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5] text-xs"
            >
              {STATUSES.map(st => <option key={st} value={st}>{st}</option>)}
            </select>
          </div>

          {/* Priority Dropdown */}
          <div className="flex items-center gap-1">
            <span className="text-[#6B7280] dark:text-[#9CA3AF] text-[11px]">Priority:</span>
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="py-1 px-2.5 rounded-lg border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5] text-xs"
            >
              {PRIORITIES.map(pr => <option key={pr} value={pr}>{pr === "All" ? "All Priorities" : `Level ${pr}`}</option>)}
            </select>
          </div>

          {/* Sort By Dropdown */}
          <div className="flex items-center gap-1 ml-auto">
            <ArrowUpDown className="w-3.5 h-3.5 text-[#6B7280]" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="py-1 px-2.5 rounded-lg border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5] text-xs"
            >
              <option value="created_at">Latest First</option>
              <option value="upvotes">Most Upvoted</option>
              <option value="priority">Highest Priority</option>
            </select>
          </div>
        </div>

        {/* Complaints Table */}
        <div className="overflow-x-auto rounded-xl border border-[#ECECE8] dark:border-[#27272A]">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#FAFAF8] dark:bg-[#131316] text-[#6B7280] dark:text-[#9CA3AF] uppercase font-semibold border-b border-[#ECECE8] dark:border-[#27272A]">
              <tr>
                <th className="py-3 px-4">Tracking ID</th>
                <th className="py-3 px-4">Grievance & Area</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status & Action</th>
                <th className="py-3 px-4 text-center">Community</th>
                <th className="py-3 px-4 text-right">Letter</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#ECECE8] dark:divide-[#27272A] text-[#111111] dark:text-[#F4F4F5]">
              {filteredComplaints.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-[#6B7280] dark:text-[#9CA3AF]">
                    No grievances match the selected filters.
                  </td>
                </tr>
              ) : (
                filteredComplaints.map((c) => (
                  <tr key={c.id} className="hover:bg-[#FAFAF8] dark:hover:bg-[#131316] transition-colors">
                    <td className="py-3.5 px-4 font-mono font-medium text-[#5B5BD6] dark:text-[#8383FF]">
                      <button 
                        onClick={() => onNavigateTrack(c.tracking_id)}
                        className="hover:underline"
                        title="Click to track in timeline"
                      >
                        {c.tracking_id}
                      </button>
                    </td>

                    <td className="py-3.5 px-4 max-w-xs">
                      <p className="font-medium truncate">{c.title}</p>
                      <span className="text-[11px] text-[#6B7280] dark:text-[#9CA3AF] flex items-center gap-1 mt-0.5">
                        <MapPin className="w-3 h-3 text-[#5B5BD6]" />
                        {c.location}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full text-[11px] font-medium bg-[#FAFAF8] dark:bg-[#1F1F24] border border-[#ECECE8] dark:border-[#27272A]">
                        {c.category}
                      </span>
                    </td>

                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            c.priority >= 4 ? 'bg-[#E5484D]' : c.priority === 3 ? 'bg-[#F2A33A]' : 'bg-[#34A874]'
                          }`}
                        />
                        <span className="font-medium text-[11px]">Level {c.priority}</span>
                      </div>
                    </td>

                    <td className="py-3.5 px-4">
                      {/* Live status dropdown in table */}
                      <select
                        value={c.status}
                        onChange={(e) => handleStatusChange(c.tracking_id, e.target.value)}
                        className="py-1 px-2 rounded-lg border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] text-xs font-medium cursor-pointer"
                      >
                        <option value="Submitted">Submitted</option>
                        <option value="Assigned">Assigned</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </td>

                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={() => handleUpvote(c.tracking_id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] text-[11px] transition-colors"
                        title="Endorse this complaint"
                      >
                        <ThumbsUp className="w-3 h-3 text-[#5B5BD6]" />
                        <span>{c.upvotes}</span>
                      </button>
                    </td>

                    <td className="py-3.5 px-4 text-right">
                      {c.formal_letter && (
                        <button
                          onClick={() => {
                            setLetterText(c.formal_letter);
                            setLetterTitle(`Official Grievance Letter (${c.tracking_id})`);
                            setLetterModalOpen(true);
                          }}
                          className="p-1.5 rounded-lg text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#5B5BD6] dark:hover:text-[#8383FF] hover:bg-[#F4F4F2] dark:hover:bg-[#202024]"
                          title="View formal letter"
                        >
                          <FileText className="w-4 h-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Formal Letter Modal */}
      <FormalLetterModal
        isOpen={letterModalOpen}
        onClose={() => setLetterModalOpen(false)}
        letterText={letterText}
        title={letterTitle}
      />
    </div>
  );
}
