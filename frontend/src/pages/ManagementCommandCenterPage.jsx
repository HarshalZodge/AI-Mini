import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  ShieldAlert, 
  Clock, 
  AlertTriangle, 
  FileCheck, 
  Users, 
  CheckCircle2, 
  Send, 
  RotateCcw,
  Sparkles,
  Layers,
  FileText,
  Printer,
  X,
  Check
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchManagementStats, updateComplaintStatus, createWorkOrder, fetchComplaints } from '../lib/api';
import FormalLetterModal from '../components/FormalLetterModal';

export default function ManagementCommandCenterPage({ onNavigateTrack }) {
  const [statsData, setStatsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('radar'); // 'radar', 'departments', 'workorders'
  const [workOrderModalOpen, setWorkOrderModalOpen] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [assignedOfficer, setAssignedOfficer] = useState('Er. S. Patil (Junior Engineer)');
  const [contractor, setContractor] = useState('M/s Pune Municipal Rapid Infra Works');
  const [instructions, setInstructions] = useState('Deploy field team and set up high-visibility barriers within 4 hours.');
  const [materials, setMaterials] = useState(['Cold Asphalt Mix', 'Safety Barricades', 'Reflective Caution Tape']);
  const [issuedDocket, setIssuedDocket] = useState(null);
  const [dispatchSuccess, setDispatchSuccess] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await fetchManagementStats();
      setStatsData(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOpenDispatchModal = (complaint) => {
    setSelectedComplaint(complaint);
    setIssuedDocket(null);
    setDispatchSuccess(false);
    setWorkOrderModalOpen(true);
  };

  const handleIssueWorkOrder = async (e) => {
    e.preventDefault();
    if (!selectedComplaint) return;

    try {
      const res = await createWorkOrder(selectedComplaint.tracking_id, {
        assigned_officer: assignedOfficer,
        contractor: contractor,
        priority_instructions: instructions,
        equipment_and_materials: materials
      });
      setIssuedDocket(res);
      setDispatchSuccess(true);
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleQuickResolve = async (trackingId) => {
    try {
      await updateComplaintStatus(trackingId, 'Resolved', 'Remediation completed on site and verified by ward supervisor.');
      await loadData();
    } catch (err) {
      console.error(err);
    }
  };

  const summary = statsData?.summary;
  const overdueAlerts = statsData?.overdue_alerts || [];
  const nearDeadline = statsData?.near_deadline || [];
  const deptPerformance = statsData?.department_performance || [];

  return (
    <div className="max-w-[1100px] mx-auto px-4 sm:px-6 py-8 min-h-[calc(100vh-4rem)] space-y-8">
      {/* Official Management Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[#ECECE8] dark:border-[#27272A]">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#111111] dark:bg-[#27272A] text-white text-xs font-semibold mb-2">
            <Building2 className="w-3.5 h-3.5 text-[#F2A33A]" />
            <span>Pune Municipal Corporation • Administrative Portal</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#111111] dark:text-[#F4F4F5] tracking-tight">
            Grievance Redressal Command Center
          </h1>
          <p className="text-xs sm:text-sm text-[#6B7280] dark:text-[#9CA3AF] mt-1">
            Ward Officer & Field Engineering Command: SLA Breach Radar, Work Order Dispatch, and Contractor Management.
          </p>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-1.5 self-start sm:self-auto px-3.5 py-2 rounded-xl text-xs font-medium border border-[#ECECE8] dark:border-[#27272A] bg-[#FFFFFF] dark:bg-[#17171A] text-[#4B5563] dark:text-[#D1D5DB] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {/* 4 Executive KPI Cards */}
      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
            <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">SLA Compliance Rate</span>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#34A874] mt-1 tracking-tight">
              {summary.sla_adherence_rate}%
            </p>
            <span className="text-[11px] text-[#6B7280] dark:text-[#9CA3AF] mt-0.5 inline-block">Citizen Charter Benchmark</span>
          </div>

          <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
            <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">Overdue SLA Breaches</span>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#E5484D] mt-1 tracking-tight">
              {summary.overdue_count}
            </p>
            <span className="text-[11px] text-[#E5484D] mt-0.5 inline-block">Requires Immediate Escalation</span>
          </div>

          <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
            <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">Active Field Dispatches</span>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#5B5BD6] dark:text-[#8383FF] mt-1 tracking-tight">
              {summary.in_progress_count}
            </p>
            <span className="text-[11px] text-[#5B5BD6] dark:text-[#8383FF] mt-0.5 inline-block">Work Orders In Execution</span>
          </div>

          <div className="p-5 rounded-2xl bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
            <span className="text-xs font-medium text-[#6B7280] dark:text-[#9CA3AF]">High Risk Hazards (P4-5)</span>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#F2A33A] mt-1 tracking-tight">
              {summary.high_risk_count}
            </p>
            <span className="text-[11px] text-[#F2A33A] mt-0.5 inline-block">Open Life-Safety Risks</span>
          </div>
        </div>
      )}

      {/* Sub-navigation tabs */}
      <div className="flex items-center gap-2 border-b border-[#ECECE8] dark:border-[#27272A] pb-3 text-xs sm:text-sm">
        <button
          onClick={() => setActiveTab('radar')}
          className={`flex items-center gap-2 pb-2 font-semibold border-b-2 transition-all ${
            activeTab === 'radar'
              ? 'border-[#5B5BD6] text-[#5B5BD6] dark:text-[#8383FF]'
              : 'border-transparent text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111]'
          }`}
        >
          <AlertTriangle className="w-4 h-4 text-[#E5484D]" />
          <span>SLA Breach Risk Radar ({overdueAlerts.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('departments')}
          className={`flex items-center gap-2 pb-2 font-semibold border-b-2 transition-all ml-4 ${
            activeTab === 'departments'
              ? 'border-[#5B5BD6] text-[#5B5BD6] dark:text-[#8383FF]'
              : 'border-transparent text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#111111]'
          }`}
        >
          <Building2 className="w-4 h-4 text-[#5B5BD6]" />
          <span>Department Performance Rankings</span>
        </button>
      </div>

      {/* TAB 1: SLA Breach Radar & Urgent Action Dispatch */}
      {activeTab === 'radar' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#FFF5F5] dark:bg-[#201012] border border-[#FCDAD7] dark:border-[#4A1D24] text-xs flex items-center justify-between">
            <div className="flex items-center gap-2.5 text-[#E5484D]">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>
                <strong>Action Alert:</strong> {overdueAlerts.length} complaints have breached or exceeded their stipulated Citizen Charter SLA. Issue field work orders below.
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {overdueAlerts.map((item) => (
              <div
                key={item.tracking_id}
                className="bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-[#5B5BD6] dark:text-[#8383FF] bg-[#EEF0FF] dark:bg-[#1C1C30] px-2 py-0.5 rounded">
                      {item.tracking_id}
                    </span>
                    <span className="text-[11px] font-semibold text-[#E5484D] bg-[#FFF5F5] dark:bg-[#2A1012] px-2 py-0.5 rounded-full border border-[#E5484D]/30">
                      Overdue by {item.days_elapsed - item.sla_days} days
                    </span>
                    <span className="text-[11px] font-medium text-[#6B7280] dark:text-[#9CA3AF]">
                      Priority {item.priority}/5
                    </span>
                    {item.escalated && (
                      <span className="text-[10px] bg-[#E5484D] text-white px-2 py-0.2 rounded font-bold">
                        ESCALATED TO COMMISSIONER
                      </span>
                    )}
                  </div>

                  <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5]">
                    {item.title}
                  </h3>

                  <p className="text-xs text-[#6B7280] dark:text-[#9CA3AF]">
                    {item.location} • <strong className="text-[#374151] dark:text-[#D1D5DB]">{item.department}</strong> (Target SLA: {item.sla_days} days)
                  </p>
                </div>

                {/* Dispatch / Quick Resolve Controls */}
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleOpenDispatchModal(item)}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-[#5B5BD6] text-white hover:bg-[#4848BD] shadow-2xs transition-all"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Issue Official Work Order</span>
                  </button>

                  <button
                    onClick={() => handleQuickResolve(item.tracking_id)}
                    className="flex items-center gap-1 px-3 py-2 rounded-xl text-xs font-medium border border-[#ECECE8] dark:border-[#27272A] hover:bg-[#EBF8F2] hover:text-[#34A874] text-[#374151] dark:text-[#D1D5DB] transition-all"
                    title="Mark resolved after inspection"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Verify & Close</span>
                  </button>

                  <button
                    onClick={() => onNavigateTrack(item.tracking_id)}
                    className="p-2 rounded-xl border border-[#ECECE8] dark:border-[#27272A] text-[#6B7280] hover:text-[#5B5BD6]"
                    title="View lifecycle track"
                  >
                    <Clock className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: Department Performance Rankings */}
      {activeTab === 'departments' && (
        <div className="bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#ECECE8] dark:border-[#27272A]">
            <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5]">
              PMC Departments Ranked by SLA On-Time Adherence
            </h3>
            <span className="text-xs text-[#6B7280] dark:text-[#9CA3AF]">
              Performance Benchmark: &ge;85%
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#FAFAF8] dark:bg-[#131316] text-[#6B7280] dark:text-[#9CA3AF] uppercase font-semibold">
                <tr>
                  <th className="py-3 px-4">Rank & Department</th>
                  <th className="py-3 px-4">Authority Title</th>
                  <th className="py-3 px-4 text-center">Total Cases</th>
                  <th className="py-3 px-4 text-center">Open Cases</th>
                  <th className="py-3 px-4 text-center">Resolved</th>
                  <th className="py-3 px-4 text-center">Target SLA</th>
                  <th className="py-3 px-4 text-right">SLA Adherence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#ECECE8] dark:divide-[#27272A]">
                {deptPerformance.map((dept, idx) => (
                  <tr key={dept.department} className="hover:bg-[#FAFAF8] dark:hover:bg-[#131316]">
                    <td className="py-3.5 px-4 font-medium flex items-center gap-2">
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] ${
                        idx === 0 ? 'bg-[#FEF3C7] text-[#D97706]' : 'bg-[#F4F4F2] dark:bg-[#202024] text-[#6B7280]'
                      }`}>
                        {idx + 1}
                      </span>
                      <span>{dept.department}</span>
                    </td>
                    <td className="py-3.5 px-4 text-[#6B7280] dark:text-[#9CA3AF] max-w-xs truncate">
                      {dept.authority}
                    </td>
                    <td className="py-3.5 px-4 text-center font-semibold">{dept.total}</td>
                    <td className="py-3.5 px-4 text-center text-[#F2A33A] font-semibold">{dept.open}</td>
                    <td className="py-3.5 px-4 text-center text-[#34A874] font-semibold">{dept.resolved}</td>
                    <td className="py-3.5 px-4 text-center font-mono">{dept.sla_days} days</td>
                    <td className="py-3.5 px-4 text-right font-bold">
                      <span className={`px-2 py-0.5 rounded-full text-[11px] ${
                        dept.compliance_pct >= 80
                          ? 'bg-[#EBF8F2] text-[#34A874]'
                          : 'bg-[#FFF5F5] text-[#E5484D]'
                      }`}>
                        {dept.compliance_pct}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Official Work Order Dispatch Modal */}
      {workOrderModalOpen && selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
          <div className="w-full max-w-2xl bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
            {/* Header */}
            <div className="px-5 py-4 border-b border-[#ECECE8] dark:border-[#27272A] flex items-center justify-between bg-[#FAFAF8] dark:bg-[#131316]">
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-[#5B5BD6]" />
                <h3 className="font-semibold text-sm text-[#111111] dark:text-[#F4F4F5]">
                  Issue Official Municipal Work Order ({selectedComplaint.tracking_id})
                </h3>
              </div>
              <button
                onClick={() => setWorkOrderModalOpen(false)}
                className="p-1 rounded-lg text-[#6B7280] hover:text-[#111111]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-4 text-xs">
              {!dispatchSuccess ? (
                <form onSubmit={handleIssueWorkOrder} className="space-y-4">
                  <div className="p-3 rounded-xl bg-[#EEF0FF]/50 dark:bg-[#1C1C30]/50 border border-[#5B5BD6]/20">
                    <p className="font-semibold text-[#5B5BD6] dark:text-[#8383FF]">
                      Grievance: {selectedComplaint.title}
                    </p>
                    <p className="text-[#6B7280] dark:text-[#9CA3AF] mt-0.5">
                      Location: {selectedComplaint.location} | Dept: {selectedComplaint.department}
                    </p>
                  </div>

                  <div>
                    <label className="font-medium text-[#111111] dark:text-[#F4F4F5] block mb-1">
                      Designated Junior Field Engineer:
                    </label>
                    <input
                      type="text"
                      value={assignedOfficer}
                      onChange={(e) => setAssignedOfficer(e.target.value)}
                      className="w-full p-2.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5]"
                      required
                    />
                  </div>

                  <div>
                    <label className="font-medium text-[#111111] dark:text-[#F4F4F5] block mb-1">
                      Contractor Agency / Rapid Works Crew:
                    </label>
                    <input
                      type="text"
                      value={contractor}
                      onChange={(e) => setContractor(e.target.value)}
                      className="w-full p-2.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5]"
                      required
                    />
                  </div>

                  <div>
                    <label className="font-medium text-[#111111] dark:text-[#F4F4F5] block mb-1">
                      Safety & Operational Scope Directives:
                    </label>
                    <textarea
                      rows={2}
                      value={instructions}
                      onChange={(e) => setInstructions(e.target.value)}
                      className="w-full p-2.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5]"
                    />
                  </div>

                  <div>
                    <label className="font-medium text-[#111111] dark:text-[#F4F4F5] block mb-1">
                      Requisitioned Materials (Comma-separated):
                    </label>
                    <input
                      type="text"
                      value={materials.join(', ')}
                      onChange={(e) => setMaterials(e.target.value.split(',').map(s => s.strip ? s.trim() : s))}
                      className="w-full p-2.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5]"
                    />
                  </div>

                  <div className="pt-2 flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => setWorkOrderModalOpen(false)}
                      className="px-4 py-2 rounded-xl border border-[#ECECE8] dark:border-[#27272A] text-[#6B7280]"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 rounded-xl bg-[#5B5BD6] text-white font-medium hover:bg-[#4848BD]"
                    >
                      Authorize & Dispatch Crew
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-4">
                  <div className="p-3 rounded-xl bg-[#EBF8F2] text-[#34A874] dark:bg-[#11271D] flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>
                      Official Work Order <strong>{issuedDocket?.work_order_id}</strong> issued. Status updated to 'In Progress'.
                    </span>
                  </div>

                  {/* Generated Work Order Docket */}
                  <div className="p-4 rounded-xl bg-[#FAFAF8] dark:bg-[#121214] border border-[#ECECE8] dark:border-[#27272A] font-mono text-[11px] whitespace-pre-wrap leading-relaxed select-text">
                    {issuedDocket?.work_order_document}
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <button
                      onClick={() => window.print()}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#ECECE8] dark:border-[#27272A] text-xs font-medium"
                    >
                      <Printer className="w-3.5 h-3.5" />
                      <span>Print Dispatch Docket</span>
                    </button>

                    <button
                      onClick={() => setWorkOrderModalOpen(false)}
                      className="px-4 py-1.5 rounded-lg bg-[#5B5BD6] text-white text-xs font-medium"
                    >
                      Done
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
