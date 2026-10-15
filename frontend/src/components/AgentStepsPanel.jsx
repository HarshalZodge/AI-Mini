import React, { useState } from 'react';
import { 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Sparkles, 
  Tag, 
  Building2, 
  ShieldAlert, 
  CopyCheck, 
  FileText, 
  Database,
  Code2
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const TOOL_ICONS = {
  classify_complaint: Tag,
  find_department: Building2,
  score_priority: ShieldAlert,
  check_duplicates: CopyCheck,
  generate_formal_letter: FileText,
  submit_complaint: Database,
  fallback_orchestrator: Sparkles,
};

export default function AgentStepsPanel({ steps = [] }) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedStep, setExpandedStep] = useState(null);

  if (!steps || steps.length === 0) return null;

  return (
    <div className="my-2.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] overflow-hidden text-xs transition-colors shadow-2xs">
      {/* Header bar */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3.5 py-2.5 flex items-center justify-between bg-[#F8F8F6] dark:bg-[#141416] hover:bg-[#F0F0EC] dark:hover:bg-[#1B1B1E] transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] flex items-center justify-center">
            <Sparkles className="w-3 h-3" />
          </div>
          <span className="font-semibold text-[#111111] dark:text-[#F4F4F5]">
            Agent Execution Trace
          </span>
          <span className="px-1.5 py-0.5 rounded-full bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] font-medium text-[10px]">
            {steps.length} {steps.length === 1 ? 'tool call' : 'tool calls'}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-[#6B7280] dark:text-[#9CA3AF]">
          <span className="text-[11px] font-medium">{isOpen ? 'Hide steps' : 'View steps'}</span>
          {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </div>
      </button>

      {/* Expanded list of tool calls */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="p-3 border-t border-[#ECECE8] dark:border-[#27272A] space-y-2"
          >
            {steps.map((step, idx) => {
              const Icon = TOOL_ICONS[step.tool_name] || CheckCircle2;
              const isDetailsOpen = expandedStep === idx;

              return (
                <div
                  key={idx}
                  className="rounded-lg p-2.5 bg-[#FAFAF8] dark:bg-[#121214] border border-[#ECECE8]/80 dark:border-[#222226]"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-start gap-2.5">
                      <div className="mt-0.5 w-4 h-4 rounded-full bg-[#EBF8F2] dark:bg-[#11271D] text-[#34A874] flex items-center justify-center shrink-0">
                        <Icon className="w-2.5 h-2.5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-[#111111] dark:text-[#F4F4F5]">
                            {step.step_name}
                          </span>
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-[#ECECE8] dark:bg-[#27272A] text-[#6B7280] dark:text-[#A1A1AA] font-mono">
                            {step.tool_name}()
                          </span>
                        </div>
                        <p className="text-[#4B5563] dark:text-[#9CA3AF] mt-0.5 leading-relaxed">
                          {step.summary}
                        </p>
                      </div>
                    </div>

                    {step.details && Object.keys(step.details).length > 0 && (
                      <button
                        onClick={() => setExpandedStep(isDetailsOpen ? null : idx)}
                        className="text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#5B5BD6] dark:hover:text-[#8383FF] p-1 rounded"
                        title="Inspect tool payload"
                      >
                        <Code2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>

                  {/* Raw tool parameters inspected */}
                  {isDetailsOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -4 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-2 p-2 rounded bg-[#111111] text-[#E5E7EB] font-mono text-[10px] overflow-x-auto"
                    >
                      <pre>{JSON.stringify(step.details, null, 2)}</pre>
                    </motion.div>
                  )}
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
