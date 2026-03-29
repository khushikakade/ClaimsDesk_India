const API_BASE = '/api';

export const api = {
  // Dashboard
  getDashboardSummary: async () => {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    return res.json();
  },
  
  getRecentClaims: async () => {
    const res = await fetch(`${API_BASE}/claims/recent`);
    return res.json();
  },

  // Claims
  getClaims: async (status = 'All') => {
    const url = new URL(`${API_BASE}/claims`, window.location.origin);
    if (status !== 'All') url.searchParams.append('status', status);
    const res = await fetch(url);
    return res.json();
  },

  getClaim: async (id) => {
    const res = await fetch(`${API_BASE}/claims/${id}`);
    if (!res.ok) throw new Error('Claim not found');
    return res.json();
  },

  takeAction: async (id, actionType, amountInr = null, rationale = null) => {
    const res = await fetch(`${API_BASE}/claims/${id}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_type: actionType, amount_inr: amountInr, rationale })
    });
    return res.json();
  },

  // Simulation
  getTasks: async () => {
    const res = await fetch(`${API_BASE}/tasks`);
    return res.json();
  },

  resetSimulation: async (taskId, seed = 0) => {
    const res = await fetch(`${API_BASE}/simulation/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task_id: taskId, seed })
    });
    return res.json();
  },

  stepSimulation: async (action) => {
    const res = await fetch(`${API_BASE}/simulation/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    });
    return res.json();
  },

  getSimulationState: async () => {
    const res = await fetch(`${API_BASE}/simulation/state`);
    return res.json();
  }
};
