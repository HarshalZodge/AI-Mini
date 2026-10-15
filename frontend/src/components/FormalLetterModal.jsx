import React, { useState } from 'react';
import { X, Copy, Check, Download, Printer, FileText } from 'lucide-react';

export default function FormalLetterModal({ isOpen, onClose, letterText, title = "Formal Grievance Letter", trackingId }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !letterText) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(letterText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    const blob = new Blob([letterText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `CivicResolve-${trackingId || 'Letter'}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs transition-opacity">
      <div 
        className="w-full max-w-2xl bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] shadow-xl overflow-hidden flex flex-col max-h-[88vh] animate-in fade-in zoom-in-95 duration-150"
      >
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-[#ECECE8] dark:border-[#27272A] flex items-center justify-between no-print">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] flex items-center justify-center">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5]">
                {title}
              </h3>
              {trackingId && (
                <span className="text-xs text-[#6B7280] dark:text-[#9CA3AF] font-mono">
                  Ref: {trackingId}
                </span>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5] hover:bg-[#F4F4F2] dark:hover:bg-[#222226]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body / Letter Content */}
        <div className="p-6 overflow-y-auto flex-1 bg-[#FAFAF8] dark:bg-[#121214] printable-letter font-mono text-xs leading-relaxed whitespace-pre-wrap select-text text-[#1F2937] dark:text-[#E5E7EB] border-y border-[#ECECE8] dark:border-[#222226]">
          {letterText}
        </div>

        {/* Modal Actions Footer */}
        <div className="px-5 py-3.5 bg-[#FFFFFF] dark:bg-[#17171A] flex items-center justify-between no-print">
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#F4F4F2] dark:hover:bg-[#222226] text-[#374151] dark:text-[#D1D5DB] transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-[#34A874]" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy Text'}</span>
            </button>

            <button
              onClick={handleDownloadTxt}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#F4F4F2] dark:hover:bg-[#222226] text-[#374151] dark:text-[#D1D5DB] transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .txt</span>
            </button>

            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#F4F4F2] dark:hover:bg-[#222226] text-[#374151] dark:text-[#D1D5DB] transition-colors"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / PDF</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-1.5 text-xs font-medium rounded-lg bg-[#5B5BD6] text-white hover:bg-[#4848BD] transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
