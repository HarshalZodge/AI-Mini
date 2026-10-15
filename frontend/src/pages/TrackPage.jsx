import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Clock, 
  MapPin, 
  Building2, 
  AlertTriangle, 
  FileText, 
  ShieldAlert, 
  ThumbsUp, 
  CheckCircle2, 
  ArrowRight,
  Flame,
  RotateCcw,
  Sparkles,
  ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import FormalLetterModal from '../components/FormalLetterModal';
import { fetchComplaint, updateComplaintStatus, escalateComplaint, upvoteComplaint } from '../lib/api';

const DEFAULT_SAMPLE_IDS = ['CR-2026-0001', 'CR-2026-0002', 'CR-2026-0005', 'CR-2026-0008', 'CR-2026-0011'];

export default function TrackPage({ initialTrackingId }) {
  const [searchId, setSearchId] = useState(initialTrackingId || 'CR-2026-0002');
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [letterModalOpen, setLetterModalOpen] = useState(false);
  const [letterModalConfig, setLetterModalConfig] = useState({ text: '', title: '' });
  const [recentIds, setRecentIds] = useState(DEFAULT_SAMPLE_IDS);

  // Load localStorage recents
  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem('civic_recent_complaints') || '[]');
      if (stored && stored.length > 0) {
        setRecentIds([...new Set([...stored, ...DEFAULT_SAMPLE_IDS])].slice(0, 7));
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  // Fetch on mount or change
  useEffect(() => {
    if (searchId) {
      handleSearch(searchId);
    }
  }, [initialTrackingId]);

  const handleSearch = async (idToSearch) => {
    const id = idToSearch || searchId;
    if (!id.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await fetchComplaint(id.trim());
      setComplaint(data);
    } catch (err) {
      console.error(err);
      setError(`No active complaint found for tracking ID "${id}".`);
      setComplaint(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvanceStatus = async (nextStatus) => {
    if (!complaint) return;
    setUpdatingStatus(true);
    try {
      const updated = await updateComplaintStatus(complaint.tracking_id, nextStatus);
      setComplaint(updated);
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleEscalate = async () => {
    if (!complaint) return;
    try {
      const res = await escalateComplaint(complaint.tracking_id, "Turnaround duration exceeded SLA target without on-site remediation.");
      setComplaint(prev => ({
        ...prev,
        escalated: true,
        escalation_letter: res.escalation_letter
      }));
      setLetterModalConfig({
        text: res.escalation_letter,
        title: `Statutory Escalation Notice (${complaint.tracking_id})`
      });
      setLetterModalOpen(true);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpvote = async () => {
    if (!complaint) return;
    try {
      const res = await upvoteComplaint(complaint.tracking_id);
      setComplaint(prev => ({ ...prev, upvotes: res.upvotes }));
    } catch (err) {
      console.error(err);
    }
  };

  // Check if overdue
  const isOverdue = complaint && !['Resolved'].includes(complaint.status) && (
    complaint.escalated || complaint.tracking_id === 'CR-2026-0002' || complaint.tracking_id === 'CR-2026-0008'
  );

  return (
    <div className="max-w-[1000px] mx-auto px-4 sm:px-6 py-8 min-h-[calc(100vh-4rem)]">
      {/* Header and Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#ECECE8] dark:border-[#27272A]">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#111111] dark:text-[#F4F4F5] tracking-tight">
            Track Grievance Status
          </h1>
          <p className="text-xs sm:text-sm text-[#6B7280] dark:text-[#9CA3AF] mt-1">
            Real-time stage progression, departmental updates, and statutory escalation.
          </p>
        </div>

        {/* Demo Mode Toggle */}
        <div className="flex items-center gap-2 self-start sm:self-auto bg-[#FAFAF8] dark:bg-[#17171A] p-1.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A]">
          <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF] px-1.5 flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-[#5B5BD6]" />
            Demo Mode
          </span>
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`w-9 h-5 flex items-center rounded-full p-1 transition-colors duration-200 ${
              demoMode ? 'bg-[#5B5BD6]' : 'bg-[#E5E7EB] dark:bg-[#2A2A2E]'
            }`}
          >
            <div
              className={`bg-white w-3 h-3 rounded-full shadow-md transform transition-transform duration-200 ${
                demoMode ? 'translate-x-4' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Search Bar & Quick Tags */}
      <div className="mt-6">
        <form
          onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
          className="flex items-center gap-2 max-w-xl"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#9CA3AF] absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              placeholder="Enter Tracking ID (e.g. CR-2026-0002)"
              className="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] text-[#111111] dark:text-[#F4F4F5] font-mono placeholder-sans focus:outline-hidden focus:ring-1 focus:ring-[#5B5BD6]"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2.5 rounded-xl bg-[#5B5BD6] text-white hover:bg-[#4848BD] font-medium text-xs transition-colors shadow-2xs"
          >
            Search
          </button>
        </form>

        {/* Quick select chips */}
        <div className="mt-3 flex items-center gap-2 flex-wrap text-xs">
          <span className="text-[#6B7280] dark:text-[#9CA3AF] text-[11px] font-medium">Quick inspect:</span>
          {recentIds.map((id) => (
            <button
              key={id}
              onClick={() => { setSearchId(id); handleSearch(id); }}
              className={`px-2.5 py-1 rounded-lg border font-mono text-[11px] transition-all ${
                searchId === id
                  ? 'bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] border-[#5B5BD6]/30 font-semibold'
                  : 'bg-[#FFFFFF] dark:bg-[#17171A] text-[#6B7280] dark:text-[#9CA3AF] border-[#ECECE8] dark:border-[#27272A] hover:border-[#5B5BD6]/30'
              }`}
            >
              {id}
            </button>
          ))}
        </div>
      </div>

      {/* Demo Controls Bar (Visible only when demoMode is toggled on) */}
      <AnimatePresence>
        {demoMode && complaint && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6 p-4 rounded-2xl bg-[#EEF0FF]/60 dark:bg-[#1A1A2E]/60 border border-[#5B5BD6]/30 text-xs"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-[#5B5BD6] dark:text-[#8383FF] flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5" />
                  Live Viva Demo Controls:
                </span>
                <span className="text-[#6B7280] dark:text-[#A1A1AA]">
                  Current Status: <strong>{complaint.status}</strong>
                </span>
              </div>

              <div className="flex items-center gap-2 flex-wrap">
                {['Submitted', 'Assigned', 'In Progress', 'Resolved'].map((st) => (
                  <button
                    key={st}
                    onClick={() => handleAdvanceStatus(st)}
                    disabled={updatingStatus || complaint.status === st}
                    className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                      complaint.status === st
                        ? 'bg-[#5B5BD6] text-white'
                        : 'bg-white dark:bg-[#17171A] border border-[#5B5BD6]/30 text-[#5B5BD6] dark:text-[#8383FF] hover:bg-[#5B5BD6] hover:text-white'
                    }`}
                  >
                    Set {st}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading & Error States */}
      {loading && (
        <div className="mt-12 text-center py-12">
          <div className="w-8 h-8 rounded-full border-2 border-[#5B5BD6] border-t-transparent animate-spin mx-auto"></div>
          <p className="mt-3 text-xs text-[#6B7280] dark:text-[#9CA3AF]">Retrieving grievance timeline...</p>
        </div>
      )}

      {error && (
        <div className="mt-8 p-4 rounded-2xl bg-[#FFF5F5] dark:bg-[#201012] border border-[#FCDAD7] dark:border-[#4A1D24] text-xs text-[#E5484D] flex items-center gap-2.5">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Grievance Details & Animated Vertical Timeline */}
      {!loading && complaint && (
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Complaint Snapshot & Overdue/Escalate Banner */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#ECECE8] dark:border-[#27272A]">
                <span className="font-mono text-base font-bold text-[#5B5BD6] dark:text-[#8383FF]">
                  {complaint.tracking_id}
                </span>
                <span className="px-2.5 py-1 rounded-full text-[11px] font-medium bg-[#FAFAF8] dark:bg-[#121214] border border-[#ECECE8] dark:border-[#27272A] text-[#111111] dark:text-[#F4F4F5]">
                  Priority {complaint.priority}/5
                </span>
              </div>

              <div>
                <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5] leading-snug">
                  {complaint.title}
                </h3>
                <p className="text-xs text-[#6B7280] dark:text-[#9CA3AF] mt-1.5 leading-relaxed">
                  {complaint.description}
                </p>
              </div>

              <div className="space-y-2 text-xs text-[#4B5563] dark:text-[#9CA3AF] pt-2 border-t border-[#ECECE8] dark:border-[#27272A]">
                <div className="flex items-start gap-2">
                  <MapPin className="w-3.5 h-3.5 text-[#5B5BD6] shrink-0 mt-0.5" />
                  <span>{complaint.location}</span>
                </div>
                <div className="flex items-start gap-2">
                  <Building2 className="w-3.5 h-3.5 text-[#6B7280] dark:text-[#9CA3AF] shrink-0 mt-0.5" />
                  <span>{complaint.department}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-3.5 h-3.5 text-[#6B7280] dark:text-[#9CA3AF] shrink-0" />
                  <span>Turnaround SLA: <strong>{complaint.expected_resolution_days} working days</strong></span>
                </div>
              </div>

              {/* Endorse / Upvote action */}
              <div className="pt-3 border-t border-[#ECECE8] dark:border-[#27272A] flex items-center justify-between">
                <button
                  onClick={handleUpvote}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] text-xs font-medium text-[#374151] dark:text-[#D1D5DB] transition-colors"
                >
                  <ThumbsUp className="w-3.5 h-3.5 text-[#5B5BD6]" />
                  <span>I Face This Too ({complaint.upvotes})</span>
                </button>

                {complaint.formal_letter && (
                  <button
                    onClick={() => {
                      setLetterModalConfig({
                        text: complaint.formal_letter,
                        title: `Formal Grievance Letter (${complaint.tracking_id})`
                      });
                      setLetterModalOpen(true);
                    }}
                    className="p-1.5 rounded-lg text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#5B5BD6] dark:hover:text-[#8383FF]"
                    title="View Formal Letter"
                  >
                    <FileText className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Overdue / Escalation Alert Box */}
            {isOverdue && (
              <div className="p-4 rounded-2xl bg-[#FFF5F5] dark:bg-[#201012] border border-[#FCDAD7] dark:border-[#4A1D24] text-xs space-y-2.5">
                <div className="flex items-center gap-2 text-[#E5484D] font-semibold">
                  <Flame className="w-4 h-4" />
                  <span>SLA Overdue Warning</span>
                </div>
                <p className="text-[#B91C1C] dark:text-[#F87171] leading-relaxed">
                  This grievance has surpassed the stipulated {complaint.expected_resolution_days}-day SLA window without full resolution.
                </p>

                {complaint.escalated ? (
                  <div className="pt-2">
                    <span className="inline-block px-2.5 py-1 rounded-md bg-[#E5484D] text-white font-medium text-[11px]">
                      Escalated to Municipal Commissioner
                    </span>
                    <button
                      onClick={() => {
                        setLetterModalConfig({
                          text: complaint.escalation_letter,
                          title: `Statutory Escalation Notice (${complaint.tracking_id})`
                        });
                        setLetterModalOpen(true);
                      }}
                      className="mt-2 block text-xs underline text-[#E5484D] hover:text-[#B91C1C]"
                    >
                      View Statutory Escalation Letter
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={handleEscalate}
                    className="w-full mt-2 py-2 px-3 rounded-xl bg-[#E5484D] hover:bg-[#C93B40] text-white font-medium text-xs shadow-xs transition-all flex items-center justify-center gap-1.5"
                  >
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Escalate to Higher Authority</span>
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Animated Vertical Stepper */}
          <div className="lg:col-span-2 bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] p-6 shadow-xs">
            <h2 className="text-sm font-bold text-[#111111] dark:text-[#F4F4F5] uppercase tracking-wider pb-4 border-b border-[#ECECE8] dark:border-[#27272A]">
              Grievance Lifecycle Progression
            </h2>

            <div className="relative mt-6 space-y-8 pl-4 sm:pl-6">
              {/* Stepper background track */}
              <div className="absolute left-[27px] sm:left-[35px] top-4 bottom-4 w-0.5 bg-[#ECECE8] dark:bg-[#27272A] -z-0" />

              {complaint.timeline && complaint.timeline.map((step, idx) => {
                const isCompleted = step.completed;
                const isCurrent = step.current;

                return (
                  <div key={idx} className="relative flex items-start gap-4 sm:gap-6 z-10">
                    {/* Circle Node */}
                    <div
                      className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
                        isCurrent
                          ? 'bg-[#5B5BD6] text-white ring-4 ring-[#EEF0FF] dark:ring-[#1C1C30] shadow-sm animate-pulse'
                          : isCompleted
                          ? 'bg-[#34A874] text-white'
                          : 'bg-[#FAFAF8] dark:bg-[#1F1F24] border border-[#ECECE8] dark:border-[#27272A] text-[#9CA3AF]'
                      }`}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-4 h-4 animate-check" />
                      ) : (
                        <span className="text-xs font-semibold">{idx + 1}</span>
                      )}
                    </div>

                    {/* Step Content */}
                    <div className="flex-1 pt-0.5">
                      <div className="flex flex-wrap items-center justify-between gap-1">
                        <span
                          className={`font-semibold text-sm ${
                            isCurrent
                              ? 'text-[#5B5BD6] dark:text-[#8383FF]'
                              : isCompleted
                              ? 'text-[#111111] dark:text-[#F4F4F5]'
                              : 'text-[#9CA3AF] dark:text-[#6B7280]'
                          }`}
                        >
                          {step.label}
                        </span>
                        <span className="text-[11px] text-[#6B7280] dark:text-[#888892] font-mono">
                          {step.date}
                        </span>
                      </div>

                      <p
                        className={`mt-1 text-xs leading-relaxed ${
                          isCompleted || isCurrent
                            ? 'text-[#4B5563] dark:text-[#9CA3AF]'
                            : 'text-[#9CA3AF] dark:text-[#52525B]'
                        }`}
                      >
                        {step.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Letter Modal */}
      <FormalLetterModal
        isOpen={letterModalOpen}
        onClose={() => setLetterModalOpen(false)}
        letterText={letterModalConfig.text}
        title={letterModalConfig.title}
        trackingId={complaint?.tracking_id}
      />
    </div>
  );
}
