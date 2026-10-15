import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from './components/Navbar';
import LandingChatPage from './pages/LandingChatPage';
import TrackPage from './pages/TrackPage';
import CommunityFeedPage from './pages/CommunityFeedPage';
import ManagementCommandCenterPage from './pages/ManagementCommandCenterPage';
import AdminDashboardPage from './pages/AdminDashboardPage';

export default function App() {
  const [portal, setPortal] = useState('citizen'); // 'citizen' or 'management'
  const [activeTab, setActiveTab] = useState('report');
  const [trackingIdTarget, setTrackingIdTarget] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('civic_theme') === 'dark' || 
      (!('civic_theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('civic_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('civic_theme', 'light');
    }
  }, [darkMode]);

  const handleNavigateTrack = (trackingId) => {
    setTrackingIdTarget(trackingId);
    setPortal('citizen');
    setActiveTab('track');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#FAFAF8] text-[#111111] dark:bg-[#0F0F10] dark:text-[#F4F4F5] transition-colors duration-200">
      {/* Top Navbar with Dual Portal Switcher */}
      <Navbar
        portal={portal}
        setPortal={setPortal}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />

      {/* Main Content Area with Page Transitions */}
      <main className="flex-1">
        <AnimatePresence mode="wait">
          {/* CITIZEN PORTAL PAGES */}
          {portal === 'citizen' && activeTab === 'report' && (
            <motion.div
              key="citizen-report"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <LandingChatPage onNavigateTrack={handleNavigateTrack} />
            </motion.div>
          )}

          {portal === 'citizen' && activeTab === 'track' && (
            <motion.div
              key="citizen-track"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <TrackPage initialTrackingId={trackingIdTarget} />
            </motion.div>
          )}

          {portal === 'citizen' && activeTab === 'community' && (
            <motion.div
              key="citizen-community"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <CommunityFeedPage onNavigateTrack={handleNavigateTrack} />
            </motion.div>
          )}

          {/* MANAGEMENT PORTAL PAGES */}
          {portal === 'management' && activeTab === 'mgmt_command' && (
            <motion.div
              key="mgmt-command"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <ManagementCommandCenterPage onNavigateTrack={handleNavigateTrack} />
            </motion.div>
          )}

          {portal === 'management' && activeTab === 'admin' && (
            <motion.div
              key="mgmt-admin"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <AdminDashboardPage onNavigateTrack={handleNavigateTrack} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Minimal Footer with Portal Context */}
      <footer className="border-t border-[#ECECE8] dark:border-[#27272A] py-6 text-center text-xs text-[#6B7280] dark:text-[#9CA3AF] no-print">
        <div className="max-w-[1100px] mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-[#111111] dark:text-[#F4F4F5]">CivicResolve</span>
            <span>—</span>
            <span>{portal === 'management' ? 'Ahilyanagar Municipal Corporation Administration Suite' : 'Citizen Grievance Redressal Agent'}</span>
          </div>
          <div className="flex items-center gap-3 text-[11px]">
            <span>{portal === 'management' ? 'Official Command Center' : 'Public Grievance Portal'}</span>
            <span>•</span>
            <span>AMC Ward Routing</span>
            <span>•</span>
            <span>College AI Mini Project</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
