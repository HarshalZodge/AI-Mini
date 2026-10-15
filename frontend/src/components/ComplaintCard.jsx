import React, { useState } from 'react';
import { 
  Building2, 
  Clock, 
  MapPin, 
  FileText, 
  ExternalLink, 
  Copy, 
  Check, 
  CheckCircle, 
  AlertTriangle 
} from 'lucide-react';

export default function ComplaintCard({ complaint, onViewLetter, onTrack }) {
  const [copied, setCopied] = useState(false);

  if (!complaint) return null;

  const copyId = () => {
    navigator.clipboard.writeText(complaint.tracking_id);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const priorityColor = 
    complaint.priority >= 4 ? 'bg-[#E5484D]' :
    complaint.priority === 3 ? 'bg-[#F2A33A]' : 'bg-[#34A874]';

  return (
    <div className="mt-3 rounded-2xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] p-5 shadow-xs transition-all hover:shadow-sm">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#ECECE8] dark:border-[#27272A]">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-bold text-[#5B5BD6] dark:text-[#8383FF] bg-[#EEF0FF] dark:bg-[#1C1C30] px-2.5 py-1 rounded-lg">
            {complaint.tracking_id}
          </span>
          <button
            onClick={copyId}
            className="p-1 rounded text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5] hover:bg-[#F4F4F2] dark:hover:bg-[#222226]"
            title="Copy Tracking ID"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[#34A874]" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Priority dots 1-5 */}
        <div className="flex items-center gap-1.5 bg-[#FAFAF8] dark:bg-[#121214] px-2.5 py-1 rounded-lg border border-[#ECECE8] dark:border-[#27272A]">
          <span className="text-[11px] font-medium text-[#6B7280] dark:text-[#9CA3AF] mr-1">
            Priority {complaint.priority}/5
          </span>
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((dot) => (
              <span
                key={dot}
                className={`w-2 h-2 rounded-full transition-all ${
                  dot <= complaint.priority ? priorityColor : 'bg-[#E5E7EB] dark:bg-[#2A2A2E]'
                }`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Main Details */}
      <div className="pt-3.5 space-y-2.5 text-xs text-[#4B5563] dark:text-[#9CA3AF]">
        <div className="flex items-start gap-2">
          <MapPin className="w-3.5 h-3.5 text-[#5B5BD6] shrink-0 mt-0.5" />
          <span className="font-medium text-[#111111] dark:text-[#F4F4F5]">
            {complaint.location}
          </span>
        </div>

        <div className="flex items-start gap-2">
          <Building2 className="w-3.5 h-3.5 text-[#6B7280] dark:text-[#9CA3AF] shrink-0 mt-0.5" />
          <span>
            {complaint.department} ({complaint.authority_title})
          </span>
        </div>

        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-[#6B7280] dark:text-[#9CA3AF] shrink-0" />
          <span>
            Citizen Charter SLA: <strong className="text-[#111111] dark:text-[#F4F4F5]">{complaint.expected_resolution_days} working days</strong>
          </span>
        </div>

        {complaint.priority_reason && (
          <p className="italic text-[11px] text-[#6B7280] dark:text-[#888892] pt-1 border-t border-[#ECECE8]/60 dark:border-[#222226]">
            "{complaint.priority_reason}"
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="mt-4 pt-3 border-t border-[#ECECE8] dark:border-[#27272A] flex flex-wrap items-center gap-2">
        {complaint.formal_letter && (
          <button
            onClick={() => onViewLetter(complaint.formal_letter, complaint.tracking_id)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#F4F4F2] dark:hover:bg-[#222226] text-[#374151] dark:text-[#D1D5DB] transition-colors"
          >
            <FileText className="w-3.5 h-3.5 text-[#5B5BD6]" />
            <span>View / Download Letter</span>
          </button>
        )}

        {onTrack && (
          <button
            onClick={() => onTrack(complaint.tracking_id)}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-[#5B5BD6] text-white hover:bg-[#4848BD] transition-all ml-auto shadow-2xs"
          >
            <span>Track Progress</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}
