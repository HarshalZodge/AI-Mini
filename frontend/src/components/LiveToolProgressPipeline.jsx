import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Tag, 
  Building2, 
  ShieldAlert, 
  CopyCheck, 
  FileText, 
  CheckCircle2, 
  Loader2 
} from 'lucide-react';
import { motion } from 'framer-motion';

const TOOL_STEPS = [
  { id: 1, label: "Classifying grievance category & issue", tool: "classify_complaint()", icon: Tag },
  { id: 2, label: "Routing to official AMC Ward Department", tool: "find_department()", icon: Building2 },
  { id: 3, label: "Scoring life-safety hazard & priority", tool: "score_priority()", icon: ShieldAlert },
  { id: 4, label: "Auditing active duplicates in Ahilyanagar", tool: "check_duplicates()", icon: CopyCheck },
  { id: 5, label: "Generating formal Citizen Charter petition", tool: "generate_formal_letter()", icon: FileText },
];

export default function LiveToolProgressPipeline() {
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  useEffect(() => {
    const timer1 = setTimeout(() => setActiveStepIndex(1), 350);
    const timer2 = setTimeout(() => setActiveStepIndex(2), 750);
    const timer3 = setTimeout(() => setActiveStepIndex(3), 1150);
    const timer4 = setTimeout(() => setActiveStepIndex(4), 1600);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98, y: 6 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.98 }}
      className="w-full max-w-md rounded-2xl border border-[#5B5BD6]/30 bg-[#FFFFFF] dark:bg-[#17171A] p-4 shadow-sm space-y-3"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-[#ECECE8] dark:border-[#27272A]">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] flex items-center justify-center">
            <Sparkles className="w-3 h-3 animate-spin" />
          </div>
          <span className="font-semibold text-xs text-[#111111] dark:text-[#F4F4F5]">
            Autonomous Tool Calling in Progress...
          </span>
        </div>
        <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF]">
          Step {Math.min(activeStepIndex + 1, TOOL_STEPS.length)} of {TOOL_STEPS.length}
        </span>
      </div>

      {/* Progress Items */}
      <div className="space-y-2">
        {TOOL_STEPS.map((step, idx) => {
          const isDone = idx < activeStepIndex;
          const isCurrent = idx === activeStepIndex;
          const Icon = step.icon;

          return (
            <motion.div
              key={step.id}
              initial={false}
              animate={{ opacity: isCurrent || isDone ? 1 : 0.4 }}
              className={`flex items-center justify-between p-2 rounded-xl text-xs transition-all ${
                isCurrent 
                  ? 'bg-[#EEF0FF]/70 dark:bg-[#1C1C30]/70 border border-[#5B5BD6]/40' 
                  : isDone
                  ? 'bg-[#FAFAF8] dark:bg-[#131316]'
                  : 'bg-transparent'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                  isDone 
                    ? 'bg-[#EBF8F2] dark:bg-[#11271D] text-[#34A874]' 
                    : isCurrent 
                    ? 'bg-[#5B5BD6] text-white animate-pulse'
                    : 'bg-[#ECECE8] dark:bg-[#27272A] text-[#9CA3AF]'
                }`}>
                  {isDone ? (
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  ) : isCurrent ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Icon className="w-2.5 h-2.5" />
                  )}
                </div>

                <span className={`font-medium ${
                  isCurrent ? 'text-[#5B5BD6] dark:text-[#8383FF]' : isDone ? 'text-[#111111] dark:text-[#F4F4F5]' : 'text-[#9CA3AF]'
                }`}>
                  {step.label}
                </span>
              </div>

              <span className="font-mono text-[10px] text-[#9CA3AF] dark:text-[#6B7280]">
                {step.tool}
              </span>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
