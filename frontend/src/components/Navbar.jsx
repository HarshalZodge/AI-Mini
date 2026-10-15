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
        {/* Logo Wordmark */}
        <div 
          onClick={() => handlePortalSwitch('citizen')}
          className="flex items-center gap-2.5 cursor-pointer group shrink-0"
        >
          <div className={`w-8 h-8 rounded-xl flex items-center justify-center text-white shadow-xs transition-transform group-hover:scale-105 ${
            isManagement ? 'bg-[#18181B] dark:bg-[#27272A] border border-[#F2A33A]/40' : 'bg-[#5B5BD6]'
          }`}>
            {isManagement ? <Building2 className="w-4 h-4 text-[#F2A33A]" /> : <ShieldCheck className="w-4 h-4" />}
          </div>
          <div className="flex flex-col">
            <div className="flex items-center">
              <span className="font-semibold text-base sm:text-lg tracking-tight text-[#111111] dark:text-[#F4F4F5]">
                Civic<span className={isManagement ? "text-[#F2A33A]" : "text-[#5B5BD6] dark:text-[#6E6EF7]"}>Resolve</span>
              </span>
              <span className={`w-1.5 h-1.5 rounded-full ml-1 mb-2 animate-pulse ${
                isManagement ? 'bg-[#F2A33A]' : 'bg-[#5B5BD6]'
              }`} />
            </div>
            <span className="text-[10px] -mt-1 font-medium text-[#6B7280] dark:text-[#9CA3AF]">
              {isManagement ? 'PMC Management Suite' : 'Citizen Grievance Redressal'}
            </span>
          </div>
        </div>

        {/* Center Navigation Links based on Active Portal */}
        <nav className="flex items-center gap-1 bg-[#FFFFFF] dark:bg-[#17171A] p-1 rounded-xl border border-[#ECECE8] dark:border-[#27272A] shadow-2xs">
          {!isManagement ? (
            // Citizen Portal Tabs
            <>
              <button
                onClick={() => setActiveTab('report')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'report'
                    ? 'bg-[#5B5BD6] text-white shadow-xs'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                <MessageSquarePlus className="w-3.5 h-3.5" />
                <span>Report</span>
              </button>

              <button
                onClick={() => setActiveTab('track')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'track'
                    ? 'bg-[#5B5BD6] text-white shadow-xs'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>Track</span>
              </button>

              <button
                onClick={() => setActiveTab('community')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'community'
                    ? 'bg-[#5B5BD6] text-white shadow-xs'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                <Users className="w-3.5 h-3.5" />
                <span>Pulse</span>
              </button>
            </>
          ) : (
            // Management Portal Tabs
            <>
              <button
                onClick={() => setActiveTab('mgmt_command')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'mgmt_command'
                    ? 'bg-[#18181B] text-white dark:bg-[#27272A] shadow-xs border border-[#F2A33A]/50'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                <AlertTriangle className="w-3.5 h-3.5 text-[#F2A33A]" />
                <span>SLA Radar & Dispatch</span>
              </button>

              <button
                onClick={() => setActiveTab('admin')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  activeTab === 'admin'
                    ? 'bg-[#18181B] text-white dark:bg-[#27272A] shadow-xs'
                    : 'text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5]'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Registry & Heatmap</span>
              </button>
            </>
          )}
        </nav>

        {/* Right side Portal Switcher & Theme */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Distinct Portal Switcher Button */}
          <button
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
          </button>

          {/* Theme Toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            aria-label="Toggle theme"
            className="p-2 rounded-xl text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111] dark:hover:text-[#F4F4F5] hover:bg-[#F4F4F2] dark:hover:bg-[#1E1E22] border border-[#ECECE8] dark:border-[#27272A] transition-all"
          >
            {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}
