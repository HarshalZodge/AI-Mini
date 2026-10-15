import React from 'react';
import { 
  Sun, 
  Moon, 
  MessageSquarePlus, 
  Activity, 
  LayoutDashboard, 
  ShieldCheck, 
  Building2, 
  Users, 
  AlertTriangle,
  ArrowRightLeft
} from 'lucide-react';
import { motion } from 'framer-motion';

export default function Navbar({ 
  portal, 
  setPortal, 
  activeTab, 
  setActiveTab, 
  darkMode, 
  setDarkMode 
}) {
  const isManagement = portal === 'management';

  const handlePortalSwitch = (newPortal) => {
    setPortal(newPortal);
    if (newPortal === 'management') {
      setActiveTab('mgmt_command');
    } else {
      setActiveTab('report');
    }
  };

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-[#FAFAF8]/90 dark:bg-[#0F0F10]/90 border-b border-[#ECECE8] dark:border-[#27272A] transition-colors">
      <div className="max-w-[1100px] mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-2 sm:gap-4">
        {/* Logo Wordmark with Animated Icon */}
        <div 
          onClick={() => handlePortalSwitch('citizen')}
          className="flex items-center gap-2.5 cursor-pointer group shrink-0"
        >
          <motion.div
            key={portal}
            initial={{ scale: 0.85, rotate: isManagement ? 15 : -15 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 380, damping: 22 }}
            className={`w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-xs transition-transform group-hover:scale-105 ${
              isManagement ? 'bg-[#18181B] dark:bg-[#27272A] border border-[#F2A33A]/40' : 'bg-[#5B5BD6]'
            }`}
          >
            {isManagement ? <Building2 className="w-4 h-4 text-[#F2A33A]" /> : <ShieldCheck className="w-4 h-4" />}
          </motion.div>
          
          <div className="flex flex-col">
            <div className="flex items-center">
              <span className="font-semibold text-base sm:text-lg tracking-tight text-[#111111] dark:text-[#F4F4F5]">
                Civic<span className={isManagement ? "text-[#F2A33A]" : "text-[#5B5BD6] dark:text-[#6E6EF7]"}>Resolve</span>
              </span>
              <span className={`w-1.5 h-1.5 rounded-full ml-1 mb-2 animate-pulse ${
                isManagement ? 'bg-[#F2A33A]' : 'bg-[#5B5BD6]'
              }`} />
            </div>
            <motion.span 
              key={portal}
              initial={{ opacity: 0, y: -2 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-[10px] -mt-1 font-medium text-[#6B7280] dark:text-[#9CA3AF]"
            >
              {isManagement ? 'PMC Management Suite' : 'Citizen Grievance Redressal'}
            </motion.span>
          </div>
        </div>

        {/* Center Navigation Links based on Active Portal */}
        <nav className="flex items-center gap-1 bg-[#FFFFFF] dark:bg-[#17171A] p-1 rounded-xl border border-[#ECECE8] dark:border-[#27272A] shadow-2xs">
          {!isManagement ? (
            // Citizen Portal Tabs
            <>
              <button
                onClick={() => setActiveTab('report')}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'report'
                    ? 'text-white'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                {activeTab === 'report' && (
                  <motion.div
                    layoutId="active-pill"
                    className="absolute inset-0 rounded-lg bg-[#5B5BD6] shadow-xs"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <MessageSquarePlus className="w-3.5 h-3.5 relative z-10" />
                <span className="relative z-10">Report</span>
              </button>

              <button
                onClick={() => setActiveTab('track')}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'track'
                    ? 'text-white'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                {activeTab === 'track' && (
                  <motion.div
                    layoutId="active-pill"
                    className="absolute inset-0 rounded-lg bg-[#5B5BD6] shadow-xs"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <Activity className="w-3.5 h-3.5 relative z-10" />
                <span className="relative z-10">Track</span>
              </button>

              <button
                onClick={() => setActiveTab('community')}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'community'
                    ? 'text-white'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                {activeTab === 'community' && (
                  <motion.div
                    layoutId="active-pill"
                    className="absolute inset-0 rounded-lg bg-[#5B5BD6] shadow-xs"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <Users className="w-3.5 h-3.5 relative z-10" />
                <span className="relative z-10">Pulse</span>
              </button>
            </>
          ) : (
            // Management Portal Tabs
            <>
              <button
                onClick={() => setActiveTab('mgmt_command')}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'mgmt_command'
                    ? 'text-white'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                {activeTab === 'mgmt_command' && (
                  <motion.div
                    layoutId="active-mgmt-pill"
                    className="absolute inset-0 rounded-lg bg-[#18181B] dark:bg-[#27272A] border border-[#F2A33A]/50 shadow-xs"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <AlertTriangle className="w-3.5 h-3.5 text-[#F2A33A] relative z-10" />
                <span className="relative z-10">SLA Radar & Dispatch</span>
              </button>

              <button
                onClick={() => setActiveTab('admin')}
                className={`relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'admin'
                    ? 'text-white'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                {activeTab === 'admin' && (
                  <motion.div
                    layoutId="active-mgmt-pill"
                    className="absolute inset-0 rounded-lg bg-[#18181B] dark:bg-[#27272A] shadow-xs"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <LayoutDashboard className="w-3.5 h-3.5 relative z-10" />
                <span className="relative z-10">Registry & Heatmap</span>
              </button>
            </>
          )}
        </nav>

        {/* Right side Portal Switcher & Theme */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Animated Morphing Portal Switcher Button */}
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.96 }}
            onClick={() => handlePortalSwitch(isManagement ? 'citizen' : 'management')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              isManagement
                ? 'bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] border-[#5B5BD6]/30 hover:bg-[#E0E4FF]'
                : 'bg-[#FFFBEB] dark:bg-[#221B10] text-[#B45309] dark:text-[#FCD34D] border-[#FCD34D]/40 hover:bg-[#FEF3C7]'
            }`}
          >
            <ArrowRightLeft className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">
              {isManagement ? 'Switch to Citizen Portal' : 'Switch to PMC Management'}
            </span>
            <span className="sm:hidden">
              {isManagement ? 'Citizen' : 'Officer'}
            </span>
          </motion.button>

          {/* Theme Toggle */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.94 }}
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle theme"
            className="p-2 rounded-xl text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5] hover:bg-[#F4F4F2] dark:hover:bg-[#1E1E22] border border-[#ECECE8] dark:border-[#27272A] transition-all"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </motion.button>
        </div>
      </div>
    </header>
  );
}
