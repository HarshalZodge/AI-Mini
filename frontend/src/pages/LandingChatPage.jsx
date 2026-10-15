import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Image as ImageIcon, 
  X, 
  Sparkles, 
  ThumbsUp, 
  Check, 
  ArrowRight,
  ShieldAlert,
  Loader2,
  FileCheck2,
  AlertCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import AgentStepsPanel from '../components/AgentStepsPanel';
import ComplaintCard from '../components/ComplaintCard';
import FormalLetterModal from '../components/FormalLetterModal';
import LiveToolProgressPipeline from '../components/LiveToolProgressPipeline';
import { sendChatMessage, analyzeImage, upvoteComplaint } from '../lib/api';

const QUICK_PROMPTS = [
  "Pothole near Paud Road, Kothrud",
  "No drinking water since morning in Baner",
  "Garbage overflowing opposite IT Park Hinjawadi",
  "Streetlights dark on JM Road Shivajinagar"
];

export default function LandingChatPage({ onNavigateTrack }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Namaste! I am **CivicResolve**, your AI civic redressal agent for Pune Municipal Corporation.\n\nDescribe any issue in **English, Hindi, or Marathi** (e.g., potholes, garbage, water supply, broken streetlights). I'll autonomously classify it, match the right department, evaluate safety priority, and draft your formal grievance letter.",
      steps: [],
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageAnalysis, setImageAnalysis] = useState(null);
  const [letterModalOpen, setLetterModalOpen] = useState(false);
  const [activeLetter, setActiveLetter] = useState({ text: '', id: '' });
  const [upvotedDups, setUpvotedDups] = useState({});

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const chatInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleImageSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      const base64 = event.target.result;
      setSelectedImage(base64);

      // Trigger vision analysis
      try {
        const analysis = await analyzeImage(base64);
        setImageAnalysis(analysis);
        // Pre-fill text if empty
        if (!inputText.trim()) {
          setInputText(`${analysis.suggested_category}: ${analysis.suggested_sub_issue} observed. ${analysis.severity_assessment}`);
        }
      } catch (err) {
        console.error('Image analysis error:', err);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleSend = async (overrideText = null) => {
    const textToSend = overrideText || inputText;
    if (!textToSend.trim() && !selectedImage) return;

    const userMessageId = `user-${Date.now()}`;
    const userMsg = {
      id: userMessageId,
      role: 'user',
      content: textToSend,
      image: selectedImage
    };

    setMessages(prev => [...prev, userMsg]);
    setInputText('');
    const curImage = selectedImage;
    setSelectedImage(null);
    setImageAnalysis(null);
    setIsLoading(true);

    try {
      // Build history for backend
      const historyPayload = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const res = await sendChatMessage(textToSend, historyPayload, curImage);

      const botMessageId = `bot-${Date.now()}`;
      const botMsg = {
        id: botMessageId,
        role: 'assistant',
        content: res.reply,
        steps: res.agent_steps || [],
        complaintDraft: res.complaint_draft,
        submittedComplaint: res.submitted_complaint,
        duplicateFound: res.duplicate_found,
        needsConfirmation: res.needs_confirmation
      };

      setMessages(prev => [...prev, botMsg]);

      // Save submitted complaints to local recent complaints & celebrate with confetti
      if (res.submitted_complaint) {
        confetti({
          particleCount: 90,
          spread: 80,
          origin: { y: 0.6 },
          colors: ['#5B5BD6', '#34A874', '#F2A33A', '#8383FF', '#10B981']
        });

        try {
          const recents = JSON.parse(localStorage.getItem('civic_recent_complaints') || '[]');
          const updated = [res.submitted_complaint.tracking_id, ...recents.filter(x => x !== res.submitted_complaint.tracking_id)].slice(0, 5);
          localStorage.setItem('civic_recent_complaints', JSON.stringify(updated));
        } catch (e) {
          console.error(e);
        }
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: "I ran into a temporary connection issue. Please check your network and try again.",
          steps: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmSubmit = () => {
    handleSend("Yes, please submit this formal complaint to the department.");
  };

  const handleUpvoteDuplicate = async (trackingId) => {
    try {
      await upvoteComplaint(trackingId);
      setUpvotedDups(prev => ({ ...prev, [trackingId]: true }));
    } catch (err) {
      console.error(err);
    }
  };

  const openLetterModal = (text, id) => {
    setActiveLetter({ text, id });
    setLetterModalOpen(true);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col justify-between max-w-[1000px] mx-auto px-4 sm:px-6 py-6">
      {/* Hero Section */}
      <section className="text-center py-6 sm:py-8">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#EEF0FF] dark:bg-[#1C1C30] text-[#5B5BD6] dark:text-[#8383FF] text-xs font-semibold mb-3 border border-[#5B5BD6]/20">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Tool-Calling AI Agent</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-[#111111] dark:text-[#F4F4F5] leading-tight sm:leading-snug">
            Your city, <span className="text-[#5B5BD6] dark:text-[#6E6EF7]">heard.</span>
          </h1>

          <p className="mt-2.5 max-w-xl mx-auto text-sm sm:text-base text-[#6B7280] dark:text-[#9CA3AF] leading-relaxed">
            Report civic grievances naturally. Our AI agent classifies the issue, calculates safety priority, prevents duplicates, and routes formal petitions to Pune Municipal Corporation.
          </p>
        </motion.div>
      </section>

      {/* Main Chat Container */}
      <div className="flex-1 flex flex-col bg-[#FFFFFF] dark:bg-[#17171A] rounded-2xl border border-[#ECECE8] dark:border-[#27272A] shadow-xs overflow-hidden min-h-[460px]">
        {/* Messages Scroll Area */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                {/* User attached photo preview */}
                {msg.image && (
                  <div className="mb-2 max-w-xs rounded-xl overflow-hidden border border-[#ECECE8] dark:border-[#27272A] shadow-xs">
                    <img src={msg.image} alt="User attachment" className="w-full h-40 object-cover" />
                  </div>
                )}

                {/* Message Bubble */}
                <div
                  className={`max-w-[85%] sm:max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-[#5B5BD6] text-white rounded-tr-xs shadow-xs'
                      : 'bg-[#FAFAF8] dark:bg-[#131316] text-[#111111] dark:text-[#F4F4F5] border border-[#ECECE8] dark:border-[#27272A] rounded-tl-xs'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>

                {/* Collapsible Agent Execution Steps */}
                {msg.steps && msg.steps.length > 0 && (
                  <div className="w-full max-w-[85%] sm:max-w-[78%]">
                    <AgentStepsPanel steps={msg.steps} />
                  </div>
                )}

                {/* Duplicate Complaint Banner */}
                {msg.duplicateFound && (
                  <div className="w-full max-w-[85%] sm:max-w-[78%] mt-2 p-3.5 rounded-xl bg-[#FFFBEB] dark:bg-[#201A10] border border-[#FDE68A] dark:border-[#423315] text-xs">
                    <div className="flex items-start gap-2.5">
                      <AlertCircle className="w-4 h-4 text-[#F2A33A] shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-semibold text-[#92400E] dark:text-[#FCD34D]">
                          Existing Similar Grievance Found Nearby
                        </p>
                        <p className="text-[#B45309] dark:text-[#FBBF24] mt-0.5">
                          "{msg.duplicateFound.title}" at {msg.duplicateFound.location} was registered as <strong>{msg.duplicateFound.tracking_id}</strong> ({msg.duplicateFound.upvotes} citizens endorsed).
                        </p>
                        <div className="mt-2.5 flex items-center gap-2">
                          <button
                            onClick={() => handleUpvoteDuplicate(msg.duplicateFound.tracking_id)}
                            disabled={upvotedDups[msg.duplicateFound.tracking_id]}
                            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg font-medium transition-all ${
                              upvotedDups[msg.duplicateFound.tracking_id]
                                ? 'bg-[#34A874] text-white'
                                : 'bg-[#F2A33A] text-white hover:bg-[#D97706]'
                            }`}
                          >
                            <ThumbsUp className="w-3 h-3" />
                            <span>
                              {upvotedDups[msg.duplicateFound.tracking_id] ? 'Upvoted! (+1)' : 'Add My Voice (Upvote)'}
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Complaint Draft Summary Card */}
                {msg.complaintDraft && !msg.submittedComplaint && (
                  <div className="w-full max-w-[85%] sm:max-w-[78%] mt-2 p-4 rounded-xl border border-[#5B5BD6]/30 bg-[#EEF0FF]/40 dark:bg-[#1C1C30]/50">
                    <div className="flex items-center justify-between pb-2 border-b border-[#5B5BD6]/20">
                      <span className="text-xs font-semibold text-[#5B5BD6] dark:text-[#8383FF] flex items-center gap-1.5">
                        <FileCheck2 className="w-4 h-4" />
                        Grievance Ready for Submission
                      </span>
                      <span className="text-[10px] font-medium bg-[#5B5BD6] text-white px-2 py-0.5 rounded-full">
                        Priority {msg.complaintDraft.priority}/5
                      </span>
                    </div>

                    <div className="mt-2.5 text-xs text-[#374151] dark:text-[#D1D5DB] space-y-1">
                      <p><strong>Category:</strong> {msg.complaintDraft.category}</p>
                      <p><strong>Department:</strong> {msg.complaintDraft.department}</p>
                      <p><strong>Location:</strong> {msg.complaintDraft.location}</p>
                      <p><strong>Official SLA:</strong> {msg.complaintDraft.expected_resolution_days} working days</p>
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-[#5B5BD6]/20 flex items-center gap-2">
                      <button
                        onClick={handleConfirmSubmit}
                        className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-[#5B5BD6] hover:bg-[#4848BD] text-white font-medium text-xs shadow-xs transition-transform active:scale-98"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Confirm & Submit to PMC</span>
                      </button>

                      <button
                        onClick={() => openLetterModal(msg.complaintDraft.formal_letter, 'DRAFT')}
                        className="py-2 px-3 rounded-lg border border-[#5B5BD6]/30 text-[#5B5BD6] dark:text-[#8383FF] hover:bg-white/60 dark:hover:bg-[#17171A] text-xs font-medium transition-colors"
                      >
                        Preview Letter
                      </button>
                    </div>
                  </div>
                )}

                {/* Submitted Complaint Card */}
                {msg.submittedComplaint && (
                  <div className="w-full max-w-[85%] sm:max-w-[78%]">
                    <ComplaintCard
                      complaint={msg.submittedComplaint}
                      onViewLetter={openLetterModal}
                      onTrack={(id) => onNavigateTrack(id)}
                    />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Live Tool Calling Execution Pipeline */}
          {isLoading && (
            <div className="flex flex-col items-start space-y-2 max-w-[85%] my-2">
              <LiveToolProgressPipeline />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Suggestion Chips */}
        {messages.length <= 2 && (
          <div className="px-4 py-2 border-t border-[#ECECE8]/80 dark:border-[#27272A]/80 bg-[#FAFAF8]/50 dark:bg-[#121214]/50 flex items-center gap-2 overflow-x-auto no-scrollbar">
            <span className="text-[11px] font-medium text-[#6B7280] dark:text-[#9CA3AF] shrink-0">Try:</span>
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                className="shrink-0 px-2.5 py-1 text-xs rounded-lg bg-[#FFFFFF] dark:bg-[#17171A] border border-[#ECECE8] dark:border-[#27272A] text-[#4B5563] dark:text-[#D1D5DB] hover:text-[#5B5BD6] hover:border-[#5B5BD6]/40 dark:hover:text-[#8383FF] transition-all"
              >
                {prompt}
              </button>
            ))}
          </div>
        )}

        {/* Selected Image Preview Bar */}
        {selectedImage && (
          <div className="px-4 py-2 bg-[#FAFAF8] dark:bg-[#131316] border-t border-[#ECECE8] dark:border-[#27272A] flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs">
              <div className="w-10 h-10 rounded-lg overflow-hidden border border-[#ECECE8] dark:border-[#27272A]">
                <img src={selectedImage} alt="Attachment" className="w-full h-full object-cover" />
              </div>
              <div>
                <span className="font-medium text-[#111111] dark:text-[#F4F4F5] flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-[#5B5BD6]" />
                  Visual Evidence Attached
                </span>
                {imageAnalysis && (
                  <span className="text-[11px] text-[#6B7280] dark:text-[#9CA3AF]">
                    Detected: {imageAnalysis.suggested_category}
                  </span>
                )}
              </div>
            </div>

            <button
              onClick={() => { setSelectedImage(null); setImageAnalysis(null); }}
              className="p-1 rounded-lg text-[#6B7280] hover:text-[#E5484D]"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Input Bar */}
        <div className="p-3 sm:p-4 bg-[#FFFFFF] dark:bg-[#17171A] border-t border-[#ECECE8] dark:border-[#27272A]">
          <form
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="flex items-center gap-2"
          >
            {/* Hidden File Input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageSelect}
              accept="image/*"
              className="hidden"
            />

            {/* Attach Image Button */}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2.5 rounded-xl border border-[#ECECE8] dark:border-[#27272A] text-[#6B7280] dark:text-[#9CA3AF] hover:text-[#5B5BD6] dark:hover:text-[#8383FF] hover:bg-[#F4F4F2] dark:hover:bg-[#202024] transition-colors"
              title="Attach photo of issue"
            >
              <ImageIcon className="w-4 h-4" />
            </button>

            {/* Text Input */}
            <input
              ref={chatInputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Describe your issue or enter location in Pune..."
              className="flex-1 py-2.5 px-4 rounded-xl border border-[#ECECE8] dark:border-[#27272A] bg-[#FAFAF8] dark:bg-[#131316] text-sm text-[#111111] dark:text-[#F4F4F5] placeholder-[#9CA3AF] focus:outline-hidden focus:ring-1 focus:ring-[#5B5BD6] dark:focus:ring-[#6E6EF7] transition-all"
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={isLoading || (!inputText.trim() && !selectedImage)}
              className="p-2.5 rounded-xl bg-[#5B5BD6] text-white hover:bg-[#4848BD] disabled:opacity-40 disabled:hover:bg-[#5B5BD6] transition-all shadow-xs"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </form>
        </div>
      </div>

      {/* Formal Letter Modal */}
      <FormalLetterModal
        isOpen={letterModalOpen}
        onClose={() => setLetterModalOpen(false)}
        letterText={activeLetter.text}
        trackingId={activeLetter.id}
      />
    </div>
  );
}
