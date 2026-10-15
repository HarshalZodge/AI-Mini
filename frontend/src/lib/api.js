/**
 * CivicResolve API Client
 */

const API_BASE = '/api';

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function sendChatMessage(message, history = [], imageData = null, locationHint = null) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history,
      image_data: imageData,
      location_hint: locationHint
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to process message');
  }
  return res.json();
}

export async function analyzeImage(imageData) {
  const res = await fetch(`${API_BASE}/analyze-image`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_data: imageData }),
  });
  if (!res.ok) throw new Error('Failed to analyze image');
  return res.json();
}

export async function fetchComplaints(params = {}) {
  const query = new URLSearchParams();
  if (params.category && params.category !== 'All') query.set('category', params.category);
  if (params.status && params.status !== 'All') query.set('status', params.status);
  if (params.priority && params.priority !== 'All') query.set('priority', params.priority);
  if (params.sortBy) query.set('sort_by', params.sortBy);

  const res = await fetch(`${API_BASE}/complaints?${query.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch complaints');
  return res.json();
}

export async function fetchComplaint(identifier) {
  const res = await fetch(`${API_BASE}/complaints/${encodeURIComponent(identifier)}`);
  if (!res.ok) throw new Error(`Complaint ${identifier} not found`);
  return res.json();
}

export async function updateComplaintStatus(identifier, newStatus, updateNote = null) {
  const res = await fetch(`${API_BASE}/complaints/${encodeURIComponent(identifier)}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus, update_note: updateNote }),
  });
  if (!res.ok) throw new Error('Failed to update status');
  return res.json();
}

export async function upvoteComplaint(identifier) {
  const res = await fetch(`${API_BASE}/complaints/${encodeURIComponent(identifier)}/upvote`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to upvote');
  return res.json();
}

export async function escalateComplaint(identifier, reason = null) {
  const res = await fetch(`${API_BASE}/complaints/${encodeURIComponent(identifier)}/escalate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error('Failed to escalate complaint');
  return res.json();
}

export async function fetchInsights() {
  const res = await fetch(`${API_BASE}/insights`);
  if (!res.ok) throw new Error('Failed to fetch insights');
  return res.json();
}

export async function reseedDatabase() {
  const res = await fetch(`${API_BASE}/seed`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to reseed database');
  return res.json();
}

export async function fetchManagementStats() {
  const res = await fetch(`${API_BASE}/management/stats`);
  if (!res.ok) throw new Error('Failed to fetch management telemetry');
  return res.json();
}

export async function createWorkOrder(identifier, payload = {}) {
  const res = await fetch(`${API_BASE}/complaints/${encodeURIComponent(identifier)}/work-order`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to issue work order');
  return res.json();
}

