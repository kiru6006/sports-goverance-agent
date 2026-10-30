import { useState, useEffect } from 'react';
import { initialMockData } from './data/mockData';
import { 
  ShieldCheck, 
  Activity, 
  Users, 
  MapPin, 
  EyeOff, 
  CheckCircle, 
  AlertTriangle, 
  Lock,
  Plus,
  Clock,
  Award,
  ChevronRight,
  Package,
  X,
  BookOpen,
  Briefcase,
  Bot,
  Sparkles,
  RefreshCw,
  Globe,
  Wifi,
  WifiOff,
  ShieldAlert,
  Terminal,
  Trash2,
  MessageSquare,
  Send,
  Phone,
  Mail,
  FileText,
  Menu,
  ChevronDown,
  ChevronLeft,
  Search,
  Compass,
  Building,
  ExternalLink
} from 'lucide-react';

interface UserContext {
  username: string;
  role: string;
  state_id: string | null;
  district_id: string | null;
  full_name: string;
}

interface SchemeRuleItem {
  id: string;
  scheme_id: string;
  version: string;
  rule_json: string;
  effective_from: string;
  effective_to?: string;
  source_document: string;
  source_page: string;
  source_clause: string;
  status: string;
  author_id: string;
  approver_id?: string;
  approved_at?: string;
}

interface SchemeItem {
  id: string;
  code: string;
  name: string;
  level: string;
  owner_body: string;
  is_placeholder: boolean;
  verify_with_ministry: boolean;
  rules: SchemeRuleItem[];
}

interface OpportunityItem {
  id: string;
  title: string;
  type: string;
  employer: string;
  slots: number;
  state_scope?: string;
  district_scope?: string;
  deadline: string;
  status: string;
}

interface EligibilityEvaluation {
  scheme_id: string;
  scheme_name: string;
  rule_version: string;
  eligible: boolean | null;
  missing_fields: string[];
  reasons: { field: string; passed: boolean; reason: string }[];
  source_refs: { source_document: string; source_page: string; source_clause: string }[];
  evaluated_at: string;
}

interface TrainerCertItem {
  id: string;
  trainer_id: string;
  course: string;
  provider: string;
  issued_on: string;
  expires_on: string;
  status: string;
  days_to_expiry: number;
}

interface Achievement {
  id: string;
  event: string;
  level: string;
  result: string;
  event_date: string;
}

interface JourneyEvent {
  id: string;
  event_type: string;
  event_date: string;
  notes: string;
  created_at: string;
}

interface Athlete {
  id: string;
  kid: string;
  name: string;
  gender: string;
  state_id: string;
  district_id: string;
  sport_name: string;
  age_band: string;
  consent_status: string;
  verification_status: string;
  is_minor: boolean;
  is_synthetic: boolean;
  rejection_reason?: string;
  rejection_report?: string;
  rejected_by?: string;
  contact_phone?: string;
  contact_email?: string;
  support_demands?: string[];
  services_offered?: string[];
  services_needed?: string[];
  coach_name?: string;
  coach_phone?: string;
  coach_email?: string;
  specialist_contact_ref?: string;
  achievements?: Achievement[];
  journey_events?: JourneyEvent[];
}

interface DirectMessage {
  id: string;
  sender_id: string;
  sender_name: string;
  sender_role: string;
  recipient_id: string;
  recipient_name: string;
  recipient_role: string;
  athlete_context_id?: string;
  message_text: string;
  sent_at: string;
  is_read: boolean;
}

interface HeatmapCell {
  sport_code: string;
  sport_name: string;
  district_id: string;
  state_id: string;
  age_band: string;
  identified_count: number | null;
  rate_per_100k: number | null;
  peer_median_rate_per_100k: number | null;
  is_suppressed: boolean;
  is_gap: boolean;
  reasons: any[];
  as_of: string;
}

interface FunnelData {
  sport_code: string | null;
  state_id: string;
  district_id: string | null;
  identified: number;
  verified: number;
  supported: number;
  progressed: number;
  identified_to_verified_pct: number;
  verified_to_supported_pct: number;
  supported_to_progressed_pct: number;
  as_of: string;
}

interface EquipmentItem {
  id: string;
  facility_id: string;
  item_name: string;
  item_type: string;
  condition: string;
  qr_code: string;
  status: string;
}

interface EquipmentLoan {
  id: string;
  item_id: string;
  item_name: string;
  borrower_type: string;
  borrower_id: string;
  issued_at: string;
  due_at: string;
  returned_at: string | null;
  condition_out: string;
  condition_in: string | null;
  is_overdue: boolean;
}

interface Facility {
  id: string;
  name: string;
  type: string;
  district_id: string;
  latitude: number;
  longitude: number;
  sports: string[];
  open_hours_monthly: number;
}

interface StateAdapter {
  id: string;
  state_id: string;
  state_name: string;
  regional_languages: string[];
  priority_sports: { sport_code: string; name: string; target_age_group: string; talent_density_target: number }[];
  local_policy_overrides: { key: string; label: string; value: string; statutory_reference: string }[];
  is_active: boolean;
  version: string;
}

interface OfflineQueueItem {
  id: string;
  client_mutation_id: string;
  athlete_id: string;
  athlete_name: string;
  field_name: string;
  field_value: any;
  queued_at: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'diagnosis' | 'registry' | 'verification' | 'equipment' | 'facilities' | 'schemes' | 'agent' | 'adapters' | 'security'>('diagnosis');
  const [currentLang, setCurrentLang] = useState<'en' | 'hi' | 'mr'>('en');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);
  const [expandedCategories, setExpandedCategories] = useState<{ [key: string]: boolean }>({
    'talent_pipeline': true,
    'infrastructure': true,
    'ai_ecosystem': true
  });

  const toggleCategory = (catKey: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [catKey]: !prev[catKey]
    }));
  };

  const [currentUser, setCurrentUser] = useState<UserContext>({
    username: 'pune_dso',
    role: 'DISTRICT_OFFICER',
    state_id: 'MH',
    district_id: 'MH-PUN',
    full_name: 'Pune District Sports Officer'
  });
  
  const [athletes, setAthletes] = useState<Athlete[]>((initialMockData as any).athletes || []);
  const [heatmapCells, setHeatmapCells] = useState<HeatmapCell[]>((initialMockData as any).heatmap || []);
  const [funnel, setFunnel] = useState<FunnelData | null>((initialMockData as any).funnel || null);
  const [equipmentItems, setEquipmentItems] = useState<EquipmentItem[]>((initialMockData as any).equipment || []);
  const [overdueLoans, setOverdueLoans] = useState<EquipmentLoan[]>((initialMockData as any).overdue || []);
  const [facilities, setFacilities] = useState<Facility[]>((initialMockData as any).facilities || []);
  const [selectedAthlete, setSelectedAthlete] = useState<Athlete | null>(null);

  // Phase 3 States
  const [schemes, setSchemes] = useState<SchemeItem[]>((initialMockData as any).schemes || []);
  const [opportunities, setOpportunities] = useState<OpportunityItem[]>((initialMockData as any).opportunities || []);
  const [trainerCerts, setTrainerCerts] = useState<TrainerCertItem[]>((initialMockData as any).trainerCerts || []);
  const [eligibilityResults, setEligibilityResults] = useState<EligibilityEvaluation[]>([]);
  const [evaluatingAthleteId, setEvaluatingAthleteId] = useState<string | null>(null);

  // Phase 4 States
  const [agentPrompt, setAgentPrompt] = useState('');
  const [agentResponse, setAgentResponse] = useState<any | null>(null);
  const [agentProposals, setAgentProposals] = useState<any[]>((initialMockData as any).agentProposals || []);
  const [isAgentLoading, setIsAgentLoading] = useState(false);

  // Phase 5 States: State Adapters & Offline PWA
  const [selectedStateManifest, setSelectedStateManifest] = useState<StateAdapter | null>((initialMockData as any).stateManifestMH || null);
  const [selectedStateId, setSelectedStateId] = useState<string>('MH');
  const [isOfflineMode, setIsOfflineMode] = useState<boolean>(false);
  const [offlineQueue, setOfflineQueue] = useState<OfflineQueueItem[]>([]);
  const [syncHistory, setSyncHistory] = useState<any[]>((initialMockData as any).syncRecords || []);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);
  const [syncOutcome, setSyncOutcome] = useState<{ applied: number; server_won: number; errors: number } | null>(null);

  // Phase 6 States: Security, ASVS L2 & Resilience
  const [auditChainStatus, setAuditChainStatus] = useState<any | null>(null);
  const [killSwitchStatus, setKillSwitchStatus] = useState<any | null>(null);
  const [chaosDrillOutput, setChaosDrillOutput] = useState<any | null>(null);
  const [isDrillRunning, setIsDrillRunning] = useState<boolean>(false);
  const [erasureFeedback, setErasureFeedback] = useState<string | null>(null);

  // Direct Messaging & Mapping States
  const [messages, setMessages] = useState<DirectMessage[]>((initialMockData as any).messages || []);
  const [activeChatRecipient, setActiveChatRecipient] = useState<{ id: string; name: string; role: string; athlete_id?: string } | null>(null);
  const [chatInputText, setChatInputText] = useState<string>('');
  const [showRejectModal, setShowRejectModal] = useState<Athlete | null>(null);
  const [rejectReasonInput, setRejectReasonInput] = useState<string>('');
  const [rejectReportInput, setRejectReportInput] = useState<string>('');
  const [activeMappingEditAthlete, setActiveMappingEditAthlete] = useState<Athlete | null>(null);
  const [demandInput, setDemandInput] = useState<string>('');
  const [serviceNeededInput, setServiceNeededInput] = useState<string>('');
  const [serviceOfferedInput, setServiceOfferedInput] = useState<string>('');

  // Go Copilot Interactive Search & Entity Navigation State
  const [isCopilotOpen, setIsCopilotOpen] = useState<boolean>(false);
  const [copilotSearchQuery, setCopilotSearchQuery] = useState<string>('');
  const [copilotChatHistory, setCopilotChatHistory] = useState<Array<{
    id: string;
    sender: 'user' | 'copilot';
    text: string;
    timestamp: string;
    links?: Array<{
      type: 'athlete' | 'facility' | 'scheme' | 'location';
      title: string;
      subtitle: string;
      id: string;
      actionTab?: 'registry' | 'facilities' | 'schemes' | 'diagnosis';
    }>;
  }>>([
    {
      id: 'welcome-1',
      sender: 'copilot',
      text: 'Hello! I am your NSIS Go Copilot. Ask me about athletes, sports facilities, district locations, institutions, or state schemes to get instant intelligence and direct profile links.',
      timestamp: 'Just now',
      links: [
        { type: 'location', title: 'Pune District (MH-PUN)', subtitle: 'Maharashtra Central Sports Hub · 18 BOX Athletes', id: 'MH-PUN', actionTab: 'diagnosis' },
        { type: 'facility', title: 'Balewadi High Performance Centre', subtitle: 'District Stadium & Boxing Ring · 320 hrs/mo', id: 'fac-1', actionTab: 'facilities' },
        { type: 'scheme', title: 'Khelo India Scholarship (KIS)', subtitle: 'National Direct DBT Scheme · Verified Status', id: 'sch-1', actionTab: 'schemes' }
      ]
    }
  ]);

  // Onboarding Modal
  const [showOnboardModal, setShowOnboardModal] = useState(false);
  const [onboardForm, setOnboardForm] = useState({
    name: '',
    dob: '2008-05-15',
    gender: 'MALE',
    state_id: 'MH',
    district_id: 'MH-PUN',
    sport_code: 'BOX',
    guardian_ref: 'Suresh Patil (Father)',
    consent_status: 'GRANTED'
  });
  const [duplicateAlert, setDuplicateAlert] = useState<{ is_duplicate: boolean; candidates: any[] } | null>(null);
  const [onboardSuccess, setOnboardSuccess] = useState<string | null>(null);

  const demoUsers: UserContext[] = [
    { username: 'admin', role: 'NATIONAL_ADMIN', state_id: null, district_id: null, full_name: 'National Director' },
    { username: 'mh_officer', role: 'STATE_OFFICER', state_id: 'MH', district_id: null, full_name: 'MH State Director' },
    { username: 'pune_dso', role: 'DISTRICT_OFFICER', state_id: 'MH', district_id: 'MH-PUN', full_name: 'Pune DSO' },
    { username: 'sonipat_dso', role: 'DISTRICT_OFFICER', state_id: 'HR', district_id: 'HR-SON', full_name: 'Sonipat DSO' },
    { username: 'pune_coach', role: 'COACH', state_id: 'MH', district_id: 'MH-PUN', full_name: 'Academy Coach' },
  ];

  const fetchData = async (user: UserContext) => {
    try {
      const [resAth, resHeat, resFun, resEq, resOver, resFac, resSch, resOpp] = await Promise.all([
        fetch('/api/v1/registry/athletes', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/pipeline/diagnosis/heatmap', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/pipeline/funnel', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/equipment/items', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/equipment/overdue', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/facilities', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/schemes', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/opportunities', { headers: { 'x-user-id': user.username } })
      ]);

      if (resAth.ok) setAthletes(await resAth.json());
      if (resHeat.ok) setHeatmapCells(await resHeat.json());
      if (resFun.ok) setFunnel(await resFun.json());
      if (resEq.ok) setEquipmentItems(await resEq.json());
      if (resOver.ok) setOverdueLoans(await resOver.json());
      if (resFac.ok) setFacilities(await resFac.json());
      if (resSch.ok) setSchemes(await resSch.json());
      if (resOpp.ok) setOpportunities(await resOpp.json());

      // Fetch trainer certs for sample trainer
      const resCert = await fetch('/api/v1/certifications/trainer/4d1272e9-35ab-4455-9254-29ce2d5ee70e', {
        headers: { 'x-user-id': user.username }
      });
      if (resCert.ok) setTrainerCerts(await resCert.json());

      // Fetch Action Proposals
      const resProp = await fetch('/api/v1/agent/proposals', {
        headers: { 'x-user-id': user.username }
      });
      if (resProp.ok) setAgentProposals(await resProp.json());

      // Phase 5: Fetch State Adapter Manifest
      const stateToLoad = user.state_id || 'MH';
      const resManifest = await fetch(`/api/v1/adapters/states/${stateToLoad}`, {
        headers: { 'x-user-id': user.username }
      });
      if (resManifest.ok) {
        setSelectedStateManifest(await resManifest.json());
        setSelectedStateId(stateToLoad);
      }

      // Phase 5: Fetch Sync Records
      const resSyncRec = await fetch('/api/v1/sync/records', {
        headers: { 'x-user-id': user.username }
      });
      if (resSyncRec.ok) setSyncHistory(await resSyncRec.json());

      // Fetch Direct Messages
      const resMsg = await fetch('/api/v1/messages', {
        headers: { 'x-user-id': user.username }
      });
      if (resMsg.ok) setMessages(await resMsg.json());
    } catch {
      // Local fallback for static hosting / GitHub Pages
      if (initialMockData) {
        const d = initialMockData as any;
        if (d.athletes) setAthletes(d.athletes);
        if (d.heatmap) setHeatmapCells(d.heatmap);
        if (d.funnel) setFunnel(d.funnel);
        if (d.equipment) setEquipmentItems(d.equipment);
        if (d.overdue) setOverdueLoans(d.overdue);
        if (d.facilities) setFacilities(d.facilities);
        if (d.schemes) setSchemes(d.schemes);
        if (d.opportunities) setOpportunities(d.opportunities);
        if (d.trainerCerts) setTrainerCerts(d.trainerCerts);
        if (d.agentProposals) setAgentProposals(d.agentProposals);
        if (d.stateManifestMH) setSelectedStateManifest(d.stateManifestMH);
        if (d.syncRecords) setSyncHistory(d.syncRecords);
        if (d.messages) setMessages(d.messages);
      }
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChatRecipient || !chatInputText.trim()) return;
    try {
      const res = await fetch('/api/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          recipient_id: activeChatRecipient.id,
          recipient_name: activeChatRecipient.name,
          recipient_role: activeChatRecipient.role,
          athlete_context_id: activeChatRecipient.athlete_id,
          message_text: chatInputText
        })
      });
      if (res.ok) {
        const newMsg = await res.json();
        setMessages(prev => [...prev, newMsg]);
        setChatInputText('');
      } else {
        alert("Failed to send direct message.");
      }
    } catch {
      alert("Network error sending message.");
    }
  };

  const handleRejectAthlete = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!showRejectModal || !rejectReasonInput.trim()) return;
    try {
      const res = await fetch(`/api/v1/registry/athletes/${showRejectModal.id}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          target_status: 'REJECTED',
          reason: rejectReasonInput,
          rejection_report: rejectReportInput || `Candidate rejected: ${rejectReasonInput}. Verification report filed by ${currentUser.full_name}.`
        })
      });
      if (res.ok) {
        alert("Athlete marked as REJECTED with rejection report stored.");
        setShowRejectModal(null);
        setRejectReasonInput('');
        setRejectReportInput('');
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Rejection failed: ${err.detail}`);
      }
    } catch {
      alert("Rejection transition error");
    }
  };

  const handleSaveProfileMapping = async (athleteId: string, demands: string[], needed: string[], offered: string[]) => {
    try {
      const res = await fetch(`/api/v1/registry/athletes/${athleteId}/profile-mapping`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          support_demands: demands,
          services_needed: needed,
          services_offered: offered
        })
      });
      if (res.ok) {
        alert("Profile services & support demands updated successfully!");
        fetchData(currentUser);
        setActiveMappingEditAthlete(null);
      } else {
        alert("Update profile mapping failed.");
      }
    } catch {
      alert("Network error saving profile mapping");
    }
  };

  const handleLoadStateManifest = async (stId: string) => {
    setSelectedStateId(stId);
    try {
      const res = await fetch(`/api/v1/adapters/states/${stId}`, {
        headers: { 'x-user-id': currentUser.username }
      });
      if (res.ok) setSelectedStateManifest(await res.json());
    } catch (err) {
      console.error(err);
    }
  };

  const handleQueueOfflineMutation = (athlete: Athlete, field: string, val: any) => {
    const queueItem: OfflineQueueItem = {
      id: crypto.randomUUID(),
      client_mutation_id: `mut-${Date.now()}-${Math.random().toString(36).substring(7)}`,
      athlete_id: athlete.id,
      athlete_name: athlete.name,
      field_name: field,
      field_value: val,
      queued_at: new Date().toISOString()
    };
    setOfflineQueue(prev => [queueItem, ...prev]);
  };

  const handleSyncOfflineBatch = async () => {
    if (offlineQueue.length === 0) return;
    setIsSyncing(true);
    setSyncOutcome(null);

    const mutations = offlineQueue.map(item => ({
      client_mutation_id: item.client_mutation_id,
      entity_type: 'ATHLETE',
      entity_id: item.athlete_id,
      field_name: item.field_name,
      field_value: item.field_value,
      client_timestamp: item.queued_at,
      client_device_id: 'dso-field-pwa-01'
    }));

    try {
      const res = await fetch('/api/v1/sync/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({ mutations })
      });
      if (res.ok) {
        const data = await res.json();
        setSyncOutcome({
          applied: data.applied_count,
          server_won: data.conflict_server_won_count,
          errors: data.error_count
        });
        setOfflineQueue([]);
        // Refresh records & athletes
        fetchData(currentUser);
      } else {
        alert("Batch sync failed to reach server.");
      }
    } catch {
      alert("Network failure during sync.");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleVerifyAuditChain = async () => {
    try {
      const res = await fetch('/api/v1/security/audit-chain/verify', {
        headers: { 'x-user-id': currentUser.username }
      });
      if (res.ok) {
        setAuditChainStatus(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFetchKillSwitch = async () => {
    try {
      const res = await fetch('/api/v1/security/killswitch', {
        headers: { 'x-user-id': currentUser.username }
      });
      if (res.ok) {
        setKillSwitchStatus(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleKillSwitch = async (disabled: boolean) => {
    try {
      const res = await fetch('/api/v1/security/killswitch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          disabled,
          reason: disabled ? "Officer manually activated emergency kill-switch" : "Officer restored operations"
        })
      });
      if (res.ok) {
        setKillSwitchStatus(await res.json());
      } else {
        const err = await res.json();
        alert(`Kill-switch toggle error: ${err.detail}`);
      }
    } catch {
      alert("Network error updating killswitch");
    }
  };

  const handleRunChaosDrill = async () => {
    setIsDrillRunning(true);
    setChaosDrillOutput(null);
    try {
      const res = await fetch('/api/v1/security/chaos-drill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username }
      });
      if (res.ok) {
        setChaosDrillOutput(await res.json());
      } else {
        const err = await res.json();
        alert(`Chaos drill failed: ${err.detail}`);
      }
    } catch {
      alert("Network error triggering chaos drill");
    } finally {
      setIsDrillRunning(false);
    }
  };

  const handleExecuteDPDPErasure = async (athId: string) => {
    if (!confirm(`Confirm statutory DPDP Act data erasure for athlete ${athId}? This will permanently redact all PII and revoke consent.`)) return;
    try {
      const res = await fetch(`/api/v1/security/dpdp/erasure/${athId}`, {
        method: 'POST',
        headers: { 'x-user-id': currentUser.username }
      });
      if (res.ok) {
        const data = await res.json();
        setErasureFeedback(`Athlete ${athId} successfully erased. Cryptographic proof: ${data.audit_hash}`);
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Erasure error: ${err.detail}`);
      }
    } catch {
      alert("Erasure request failed");
    }
  };

  const handleAgentQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!agentPrompt.trim()) return;
    setIsAgentLoading(true);
    setAgentResponse(null);
    try {
      const res = await fetch('/api/v1/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({ prompt: agentPrompt })
      });
      if (res.ok) {
        const data = await res.json();
        setAgentResponse(data);
        fetchData(currentUser);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsAgentLoading(false);
    }
  };

  const handleExecuteProposal = async (proposalId: string, token: string) => {
    try {
      const res = await fetch(`/api/v1/agent/proposals/${proposalId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          approval_token: token,
          approval_notes: `Sanctioned by ${currentUser.full_name} (${currentUser.role})`
        })
      });
      if (res.ok) {
        alert("Proposal executed successfully with cryptographic audit logging!");
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Execution failed: ${err.detail}`);
      }
    } catch {
      alert("Execution error");
    }
  };

  useEffect(() => {
    fetchData(currentUser);
  }, [currentUser]);

  const evaluateAthleteEligibility = async (athId: string) => {
    setEvaluatingAthleteId(athId);
    try {
      const res = await fetch(`/api/v1/eligibility/athlete/${athId}`, {
        headers: { 'x-user-id': currentUser.username }
      });
      if (res.ok) {
        setEligibilityResults(await res.json());
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApproveRule = async (ruleId: string) => {
    try {
      const res = await fetch(`/api/v1/schemes/rules/${ruleId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({ rule_id: ruleId, approval_reason: 'Sanctioned under State Policy Guidelines' })
      });
      if (res.ok) {
        alert("Rule approved successfully!");
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Approval rejected: ${err.detail}`);
      }
    } catch {
      alert("Error approving rule");
    }
  };

  const handleApplyOpportunity = async (oppId: string, athId: string) => {
    try {
      const res = await fetch('/api/v1/opportunities/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          opportunity_id: oppId,
          athlete_id: athId,
          status_reason: 'Applied via District Sports Officer recommendation'
        })
      });
      if (res.ok) {
        alert("Application submitted! Transactional outbox notification queued.");
      } else {
        const err = await res.json();
        alert(`Application error: ${err.detail}`);
      }
    } catch {
      alert("Application failed");
    }
  };

  useEffect(() => {
    fetchData(currentUser);
  }, [currentUser]);

  const viewAthleteProfile = async (athId: string) => {
    try {
      const res = await fetch(`/api/v1/registry/athletes/${athId}`, {
        headers: { 'x-user-id': currentUser.username }
      });
      if (res.ok) setSelectedAthlete(await res.json());
      else {
        // Fallback to local mock athlete if offline
        const localAth = athletes.find(a => a.id === athId || a.kid === athId);
        if (localAth) setSelectedAthlete(localAth);
      }
    } catch {
      const localAth = athletes.find(a => a.id === athId || a.kid === athId);
      if (localAth) setSelectedAthlete(localAth);
    }
  };

  const handleCopilotSearch = (queryText: string) => {
    const q = queryText.trim().toLowerCase();
    if (!q) return;

    const userMsgId = `user-${Date.now()}`;
    const copilotMsgId = `copilot-${Date.now()}`;

    // Search athletes
    const matchedAthletes = athletes.filter(a => 
      a.name.toLowerCase().includes(q) || 
      a.kid.toLowerCase().includes(q) || 
      a.sport_name.toLowerCase().includes(q) ||
      a.district_id.toLowerCase().includes(q)
    );

    // Search facilities / institutes
    const matchedFacilities = facilities.filter(f => 
      f.name.toLowerCase().includes(q) || 
      f.type.toLowerCase().includes(q) || 
      f.district_id.toLowerCase().includes(q) ||
      f.sports.some(s => s.toLowerCase().includes(q))
    );

    // Search schemes
    const matchedSchemes = schemes.filter(s => 
      s.name.toLowerCase().includes(q) || 
      s.code.toLowerCase().includes(q) || 
      s.owner_body.toLowerCase().includes(q)
    );

    const links: Array<{
      type: 'athlete' | 'facility' | 'scheme' | 'location';
      title: string;
      subtitle: string;
      id: string;
      actionTab?: 'registry' | 'facilities' | 'schemes' | 'diagnosis';
    }> = [];

    matchedAthletes.slice(0, 3).forEach(ath => {
      links.push({
        type: 'athlete',
        title: `${ath.name} (${ath.kid})`,
        subtitle: `${ath.sport_name} · ${ath.age_band} · ${ath.district_id} · ${ath.verification_status}`,
        id: ath.id,
        actionTab: 'registry'
      });
    });

    matchedFacilities.slice(0, 2).forEach(fac => {
      links.push({
        type: 'facility',
        title: fac.name,
        subtitle: `${fac.type} · ${fac.district_id} · ${fac.open_hours_monthly} hrs/mo`,
        id: fac.id,
        actionTab: 'facilities'
      });
    });

    matchedSchemes.slice(0, 2).forEach(sch => {
      links.push({
        type: 'scheme',
        title: `${sch.name} (${sch.code})`,
        subtitle: `${sch.level} Level · ${sch.owner_body}`,
        id: sch.id,
        actionTab: 'schemes'
      });
    });

    // Location / District match
    if (q.includes('pune') || q.includes('mh-pun') || q.includes('maharashtra') || q.includes('nagpur')) {
      links.push({
        type: 'location',
        title: 'Maharashtra Sports Grid (MH)',
        subtitle: 'Pune (MH-PUN) & Nagpur (MH-NAG) · Heatmap & Gaps',
        id: 'MH-PUN',
        actionTab: 'diagnosis'
      });
    }

    let replyText = '';
    if (links.length > 0) {
      replyText = `Found ${links.length} matching entity record(s) for "${queryText}". Click any link below to directly open the profile, location, or institution:`;
    } else {
      replyText = `I searched the NSIS network registry for "${queryText}". No exact match was found in the current scoped database. Try searching for "Aarav", "Pooja", "Balewadi", "Boxing", "Scholarship", or "Pune".`;
      links.push({
        type: 'location',
        title: 'Explore District Pipeline Heatmap',
        subtitle: 'Navigate to Sports Pipeline Gaps across all districts',
        id: 'MH-PUN',
        actionTab: 'diagnosis'
      });
    }

    setCopilotChatHistory(prev => [
      ...prev,
      {
        id: userMsgId,
        sender: 'user',
        text: queryText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      },
      {
        id: copilotMsgId,
        sender: 'copilot',
        text: replyText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        links
      }
    ]);

    setCopilotSearchQuery('');
  };

  const handleCopilotLinkClick = (link: {
    type: string;
    id: string;
    actionTab?: 'registry' | 'facilities' | 'schemes' | 'diagnosis';
  }) => {
    if (link.actionTab) {
      setActiveTab(link.actionTab);
    }
    if (link.type === 'athlete') {
      viewAthleteProfile(link.id);
    }
    setIsCopilotOpen(false);
  };

  const checkDuplicateAndSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setDuplicateAlert(null);
    setOnboardSuccess(null);

    try {
      const dupRes = await fetch('/api/v1/registry/athletes/check-duplicate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({
          name: onboardForm.name,
          dob: onboardForm.dob,
          district_id: onboardForm.district_id
        })
      });
      const dupData = await dupRes.json();
      if (dupData.is_duplicate_candidate && !duplicateAlert) {
        setDuplicateAlert({ is_duplicate: true, candidates: dupData.candidates });
        return;
      }
    } catch (err) {
      console.error(err);
    }

    try {
      const res = await fetch('/api/v1/registry/athletes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify(onboardForm)
      });
      if (res.ok) {
        const created = await res.json();
        setOnboardSuccess(`Successfully onboarded athlete: ${created.kid}`);
        setShowOnboardModal(false);
        setDuplicateAlert(null);
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch {
      alert("Submission error");
    }
  };

  const handleVerificationAction = async (athleteId: string, targetStatus: string, reason: string) => {
    try {
      const res = await fetch(`/api/v1/registry/athletes/${athleteId}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify({ target_status: targetStatus, reason })
      });
      if (res.ok) {
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Verification rejected: ${err.detail}`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-100 text-slate-800 antialiased">
      {/* Mobile Backdrop Overlay */}
      {isMobileSidebarOpen && (
        <div 
          onClick={() => setIsMobileSidebarOpen(false)}
          className="fixed inset-0 bg-navy-950/70 z-40 lg:hidden backdrop-blur-xs transition-opacity"
        />
      )}

      {/* Left-Side Auditable Navigation Bar */}
      <aside 
        className={`fixed lg:sticky top-0 h-screen z-50 bg-slate-900 text-slate-100 flex flex-col border-r border-slate-800 transition-all duration-300 ease-in-out select-none shadow-2xl ${
          isMobileSidebarOpen ? 'translate-x-0 w-72' : '-translate-x-full lg:translate-x-0'
        } ${isSidebarCollapsed ? 'lg:w-20' : 'lg:w-72'}`}
      >
        {/* Brand & Collapse Header */}
        <div className="p-4 border-b border-slate-800/80 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/25 flex items-center justify-center shrink-0 shadow-inner">
              <ShieldCheck className="w-6 h-6 text-amber-400" />
            </div>
            {(!isSidebarCollapsed || isMobileSidebarOpen) && (
              <div className="truncate">
                <h1 className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
                  TrackNet <span className="text-[10px] bg-amber-500/20 text-amber-300 px-1.5 py-0.5 rounded font-mono font-semibold tracking-normal border border-amber-500/30">NSIS</span>
                </h1>
                <p className="text-[11px] text-slate-400 truncate">Sports Governance Platform</p>
              </div>
            )}
          </div>
          
          <button
            onClick={() => {
              if (window.innerWidth < 1024) {
                setIsMobileSidebarOpen(false);
              } else {
                setIsSidebarCollapsed(!isSidebarCollapsed);
              }
            }}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            title={isSidebarCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isSidebarCollapsed ? <ChevronRight className="w-5 h-5 hidden lg:block" /> : <ChevronLeft className="w-5 h-5 hidden lg:block" />}
            <X className="w-5 h-5 lg:hidden" />
          </button>
        </div>

        {/* User Scope & Active Role Badge */}
        {(!isSidebarCollapsed || isMobileSidebarOpen) && (
          <div className="px-4 py-3 bg-slate-950/40 border-b border-slate-800/60 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">Active Scope</span>
              <span className="text-[10px] bg-amber-400/15 text-amber-300 border border-amber-400/30 px-2 py-0.5 rounded-full font-mono font-medium">
                {currentUser.district_id || currentUser.state_id || 'ALL INDIA'}
              </span>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-xs font-bold text-amber-300 shadow-xs">
                {currentUser.full_name.charAt(0)}
              </div>
              <div className="truncate text-xs">
                <div className="font-semibold text-slate-100 truncate">{currentUser.full_name}</div>
                <div className="text-[10px] text-slate-400 font-medium">{currentUser.role}</div>
              </div>
            </div>
          </div>
        )}

        {/* Categorized Nav Menu */}
        <div className="flex-1 overflow-y-auto py-3 px-3 space-y-5 text-xs font-medium scrollbar-thin">
          
          {/* CATEGORY 1: Talent Pipeline & Verification */}
          <div className="space-y-1">
            {(!isSidebarCollapsed || isMobileSidebarOpen) ? (
              <button 
                onClick={() => toggleCategory('talent_pipeline')}
                className="w-full flex items-center justify-between px-2.5 py-1.5 text-[10px] font-bold text-slate-400 hover:text-slate-200 uppercase tracking-wider transition-colors"
              >
                <span className="flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-amber-400" /> Talent & Registry
                </span>
                <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${expandedCategories['talent_pipeline'] ? 'rotate-180' : ''}`} />
              </button>
            ) : (
              <div className="w-full h-px bg-slate-800 my-2" />
            )}

            {(expandedCategories['talent_pipeline'] || isSidebarCollapsed) && (
              <div className="space-y-1">
                {/* Pipeline Diagnosis */}
                <button
                  onClick={() => { setActiveTab('diagnosis'); setIsMobileSidebarOpen(false); }}
                  title="Pipeline Diagnosis & Gaps"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'diagnosis'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <Activity className={`w-4 h-4 shrink-0 ${activeTab === 'diagnosis' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && <span>Pipeline Diagnosis</span>}
                </button>

                {/* Unified Registry */}
                <button
                  onClick={() => { setActiveTab('registry'); setIsMobileSidebarOpen(false); }}
                  title="Unified Athlete Registry"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'registry'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <Users className={`w-4 h-4 shrink-0 ${activeTab === 'registry' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && (
                    <div className="flex-1 flex items-center justify-between">
                      <span>Unified Registry</span>
                      <span className="text-[10px] bg-slate-800 text-slate-300 border border-slate-700 px-1.5 py-0.2 rounded font-mono">
                        {athletes.length}
                      </span>
                    </div>
                  )}
                </button>

                {/* Verification Queue */}
                <button
                  onClick={() => { setActiveTab('verification'); setIsMobileSidebarOpen(false); }}
                  title="Verification Queue"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'verification'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <CheckCircle className={`w-4 h-4 shrink-0 ${activeTab === 'verification' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && (
                    <div className="flex-1 flex items-center justify-between">
                      <span>Verification Queue</span>
                      {athletes.filter(a => a.verification_status !== 'VERIFIED').length > 0 && (
                        <span className="bg-amber-400/20 text-amber-300 border border-amber-400/40 font-bold px-1.5 py-0.2 rounded-full text-[10px]">
                          {athletes.filter(a => a.verification_status !== 'VERIFIED').length}
                        </span>
                      )}
                    </div>
                  )}
                </button>

                {/* Schemes & Opportunities */}
                <button
                  onClick={() => { setActiveTab('schemes'); setIsMobileSidebarOpen(false); }}
                  title="Schemes & Opportunities"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'schemes'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <BookOpen className={`w-4 h-4 shrink-0 ${activeTab === 'schemes' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && <span>Schemes & Linkages</span>}
                </button>
              </div>
            )}
          </div>

          {/* CATEGORY 2: Facilities & Logistics */}
          <div className="space-y-1">
            {(!isSidebarCollapsed || isMobileSidebarOpen) ? (
              <button 
                onClick={() => toggleCategory('infrastructure')}
                className="w-full flex items-center justify-between px-2.5 py-1.5 text-[10px] font-bold text-slate-400 hover:text-slate-200 uppercase tracking-wider transition-colors"
              >
                <span className="flex items-center gap-1.5">
                  <Package className="w-3.5 h-3.5 text-blue-400" /> Infrastructure
                </span>
                <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${expandedCategories['infrastructure'] ? 'rotate-180' : ''}`} />
              </button>
            ) : (
              <div className="w-full h-px bg-slate-800 my-2" />
            )}

            {(expandedCategories['infrastructure'] || isSidebarCollapsed) && (
              <div className="space-y-1">
                {/* Equipment Inventory */}
                <button
                  onClick={() => { setActiveTab('equipment'); setIsMobileSidebarOpen(false); }}
                  title="Equipment Inventory"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'equipment'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <Package className={`w-4 h-4 shrink-0 ${activeTab === 'equipment' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && (
                    <div className="flex-1 flex items-center justify-between">
                      <span>Equipment Inventory</span>
                      {overdueLoans.length > 0 && (
                        <span className="bg-red-500/20 text-red-300 border border-red-500/40 px-1.5 py-0.2 rounded font-bold text-[10px]">
                          {overdueLoans.length} Overdue
                        </span>
                      )}
                    </div>
                  )}
                </button>

                {/* Facilities */}
                <button
                  onClick={() => { setActiveTab('facilities'); setIsMobileSidebarOpen(false); }}
                  title="Facilities & Venues"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'facilities'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <MapPin className={`w-4 h-4 shrink-0 ${activeTab === 'facilities' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && <span>Facilities & Venues</span>}
                </button>
              </div>
            )}
          </div>

          {/* CATEGORY 3: AI Ecosystem & Security */}
          <div className="space-y-1">
            {(!isSidebarCollapsed || isMobileSidebarOpen) ? (
              <button 
                onClick={() => toggleCategory('ai_ecosystem')}
                className="w-full flex items-center justify-between px-2.5 py-1.5 text-[10px] font-bold text-slate-400 hover:text-slate-200 uppercase tracking-wider transition-colors"
              >
                <span className="flex items-center gap-1.5">
                  <Bot className="w-3.5 h-3.5 text-cyan-400" /> AI & Security
                </span>
                <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${expandedCategories['ai_ecosystem'] ? 'rotate-180' : ''}`} />
              </button>
            ) : (
              <div className="w-full h-px bg-slate-800 my-2" />
            )}

            {(expandedCategories['ai_ecosystem'] || isSidebarCollapsed) && (
              <div className="space-y-1">
                {/* AI Agent & Policy RAG */}
                <button
                  onClick={() => { setActiveTab('agent'); setIsMobileSidebarOpen(false); }}
                  title="AI Agent & Policy RAG"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'agent'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <Bot className={`w-4 h-4 shrink-0 ${activeTab === 'agent' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && <span>AI Policy Agent</span>}
                </button>

                {/* State Adapters & Offline PWA */}
                <button
                  onClick={() => { setActiveTab('adapters'); setIsMobileSidebarOpen(false); }}
                  title="State Adapters & Offline PWA"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'adapters'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <Globe className={`w-4 h-4 shrink-0 ${activeTab === 'adapters' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && (
                    <div className="flex-1 flex items-center justify-between">
                      <span>State Adapters & PWA</span>
                      {offlineQueue.length > 0 && (
                        <span className="bg-amber-400 text-slate-950 font-bold px-1.5 py-0.2 rounded-full text-[10px]">
                          {offlineQueue.length}
                        </span>
                      )}
                    </div>
                  )}
                </button>

                {/* Security & ASVS Resilience */}
                <button
                  onClick={() => {
                    setActiveTab('security');
                    setIsMobileSidebarOpen(false);
                    handleVerifyAuditChain();
                    handleFetchKillSwitch();
                  }}
                  title="Security & ASVS Resilience"
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all ${
                    activeTab === 'security'
                      ? 'bg-amber-500/15 text-amber-300 border border-amber-500/35 font-semibold shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
                  }`}
                >
                  <ShieldAlert className={`w-4 h-4 shrink-0 ${activeTab === 'security' ? 'text-amber-400' : 'text-slate-400'}`} />
                  {(!isSidebarCollapsed || isMobileSidebarOpen) && <span>Security & ASVS</span>}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Footer Controls: Direct Chat Shortcut */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/50">
          <button
            onClick={() => {
              setActiveChatRecipient({
                id: 'support@sportsauthority.gov.in',
                name: 'Network Sports Desk',
                role: 'COORDINATOR'
              });
              setIsMobileSidebarOpen(false);
            }}
            className={`w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 rounded-xl transition-all font-semibold text-xs shadow-xs ${
              isSidebarCollapsed && !isMobileSidebarOpen ? 'px-0' : ''
            }`}
            title="Open Sports Network Messaging"
          >
            <MessageSquare className="w-4 h-4 text-amber-400" />
            {(!isSidebarCollapsed || isMobileSidebarOpen) && <span>Direct Messaging</span>}
          </button>
        </div>
      </aside>

      {/* Main Workspace with Top Header Bar */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50">
        {/* Crisp Top Bar with High Contrast Header */}
        <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-4 sm:px-6 lg:px-8 py-3.5 shadow-xs">
          <div className="flex items-center justify-between gap-4">
            
            {/* Left: Mobile Menu Toggle & Current Section Title */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsMobileSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors border border-slate-200"
                title="Open Navigation Menu"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div>
                <h2 className="text-base sm:text-lg font-bold text-slate-900 capitalize flex items-center gap-2">
                  {activeTab === 'diagnosis' && 'Pipeline Diagnosis & Gaps'}
                  {activeTab === 'registry' && 'Unified Athlete Registry'}
                  {activeTab === 'schemes' && 'Schemes & Opportunities Linkages'}
                  {activeTab === 'verification' && 'District Verification Workbench'}
                  {activeTab === 'equipment' && 'Equipment & Asset Inventory'}
                  {activeTab === 'facilities' && 'Training Facilities & Venues'}
                  {activeTab === 'agent' && 'Autonomous AI Agent & Policy RAG'}
                  {activeTab === 'adapters' && 'State Adapters & Offline PWA'}
                  {activeTab === 'security' && 'Security, Kill-Switch & Resilience'}
                </h2>
                <p className="text-[11px] text-slate-500 font-medium hidden sm:block">
                  National Sports Information System · Microservices Architecture
                </p>
              </div>
            </div>

            {/* Right: Language, Offline Mode Simulator, Role & Scope Context */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Language Switcher */}
              <div className="flex items-center bg-slate-100 border border-slate-200 rounded-lg px-2 py-1 text-xs text-slate-700 font-medium shadow-2xs">
                <Globe className="w-3.5 h-3.5 mr-1 text-slate-500" />
                <select
                  className="bg-transparent text-slate-800 font-semibold outline-none border-none text-xs cursor-pointer"
                  value={currentLang}
                  onChange={(e) => setCurrentLang(e.target.value as any)}
                >
                  <option value="en">English (EN)</option>
                  <option value="hi">हिन्दी (HI)</option>
                  <option value="mr">मराठी (MR)</option>
                </select>
              </div>

              {/* Offline PWA Simulator Toggle */}
              <button
                onClick={() => setIsOfflineMode(!isOfflineMode)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all border shadow-2xs ${
                  isOfflineMode 
                    ? 'bg-amber-50 text-amber-800 border-amber-300'
                    : 'bg-emerald-50 text-emerald-800 border-emerald-300'
                }`}
                title="Simulate offline field connectivity for PWA"
              >
                {isOfflineMode ? (
                  <>
                    <WifiOff className="w-3.5 h-3.5 text-amber-600 animate-pulse" />
                    <span className="hidden sm:inline">Offline ({offlineQueue.length})</span>
                  </>
                ) : (
                  <>
                    <Wifi className="w-3.5 h-3.5 text-emerald-600" />
                    <span className="hidden sm:inline">Online</span>
                  </>
                )}
              </button>

              {/* Role Switcher */}
              <div className="flex items-center bg-slate-100 border border-slate-200 rounded-lg px-2 py-1 text-xs shadow-2xs">
                <span className="text-slate-500 mr-1.5 hidden md:inline font-medium">User:</span>
                <select
                  className="bg-transparent text-slate-900 font-bold outline-none border-none cursor-pointer text-xs"
                  value={currentUser.username}
                  onChange={(e) => {
                    const u = demoUsers.find(x => x.username === e.target.value);
                    if (u) setCurrentUser(u);
                  }}
                >
                  {demoUsers.map(u => (
                    <option key={u.username} value={u.username}>
                      {u.full_name} ({u.role})
                    </option>
                  ))}
                </select>
              </div>

              {/* Go Copilot Search & Intelligence Button */}
              <button
                onClick={() => setIsCopilotOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold text-xs shadow-xs hover:shadow-sm transition-all transform hover:-translate-y-0.5 cursor-pointer"
                title="Open Go Copilot intelligent entity search & assistant"
              >
                <Compass className="w-4 h-4 text-slate-950 animate-spin-slow" />
                <span className="font-extrabold tracking-wide">Go Copilot</span>
              </button>
            </div>
          </div>
        </header>

        {/* Content Workspace */}
        <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
          {onboardSuccess && (
            <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm flex items-center justify-between">
              <span>{onboardSuccess}</span>
              <button onClick={() => setOnboardSuccess(null)} className="text-emerald-600 hover:text-emerald-900"><X className="w-4 h-4" /></button>
            </div>
          )}

        {/* Phase 2: Pipeline Diagnosis, Gap Heatmap & Conversion Funnel */}
        {activeTab === 'diagnosis' && (
          <div className="space-y-6">
            {/* Conversion Funnel Banner */}
            {funnel && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">Cumulative Athlete Conversion Funnel</h3>
                    <p className="text-xs text-slate-500">
                      Scope: {funnel.district_id || funnel.state_id} · Invariant: Identified ≥ Verified ≥ Supported ≥ Progressed
                    </p>
                  </div>
                  <span className="text-xs text-slate-400">As of: {new Date(funnel.as_of).toLocaleDateString()}</span>
                </div>

                <div className="grid grid-cols-4 gap-3 text-center">
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <div className="text-xs text-slate-500 font-medium">1. Identified</div>
                    <div className="text-2xl font-bold text-slate-800 my-1">{funnel.identified}</div>
                    <div className="text-[11px] text-slate-400">100% of pipeline</div>
                  </div>

                  <div className="bg-blue-50/50 p-3 rounded-xl border border-blue-200">
                    <div className="text-xs text-blue-700 font-medium">2. Verified</div>
                    <div className="text-2xl font-bold text-blue-600 my-1">{funnel.verified}</div>
                    <div className="text-[11px] text-blue-600 font-semibold">{funnel.identified_to_verified_pct}% conversion</div>
                  </div>

                  <div className="bg-emerald-50/50 p-3 rounded-xl border border-emerald-200">
                    <div className="text-xs text-emerald-700 font-medium">3. Supported</div>
                    <div className="text-2xl font-bold text-emerald-600 my-1">{funnel.supported}</div>
                    <div className="text-[11px] text-emerald-600 font-semibold">{funnel.verified_to_supported_pct}% conversion</div>
                  </div>

                  <div className="bg-amber-50/50 p-3 rounded-xl border border-amber-200">
                    <div className="text-xs text-amber-700 font-medium">4. Progressed</div>
                    <div className="text-2xl font-bold text-amber-600 my-1">{funnel.progressed}</div>
                    <div className="text-[11px] text-amber-600 font-semibold">{funnel.supported_to_progressed_pct}% conversion</div>
                  </div>
                </div>
              </div>
            )}

            {/* Gap Heatmap */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">District Gap Diagnosis Matrix</h3>
                  <p className="text-xs text-slate-500">
                    Compares identified athletes per 100,000 population against state peer median.
                  </p>
                </div>
                <div className="text-xs font-semibold text-slate-500 bg-slate-200/80 px-2.5 py-1 rounded-md">
                  Policy Guideline: Not a district performance ranking
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {heatmapCells.map((cell, idx) => (
                  <div 
                    key={idx} 
                    className={`rounded-xl border p-5 shadow-sm space-y-3 ${
                      cell.is_gap ? 'bg-red-50/40 border-red-200' : 'bg-white border-slate-200'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-xs uppercase tracking-wider font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                          {cell.sport_name} ({cell.sport_code})
                        </span>
                        <h4 className="font-bold text-slate-900 mt-1">
                          District: {cell.district_id} · Age Band: {cell.age_band}
                        </h4>
                      </div>

                      {cell.is_suppressed ? (
                        <span className="inline-flex items-center gap-1 text-xs text-slate-600 bg-slate-100 border border-slate-300 px-2 py-1 rounded">
                          <EyeOff className="w-3.5 h-3.5" /> Suppressed (&lt;5)
                        </span>
                      ) : cell.is_gap ? (
                        <span className="inline-flex items-center gap-1 text-xs text-red-700 bg-red-100 border border-red-300 px-2 py-1 rounded font-semibold">
                          <AlertTriangle className="w-3.5 h-3.5" /> Pipeline Gap Flag
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded font-medium">
                          <CheckCircle className="w-3.5 h-3.5" /> Adequate Coverage
                        </span>
                      )}
                    </div>

                    {cell.is_suppressed ? (
                      <div className="p-4 bg-slate-50 rounded-lg text-center text-xs text-slate-500 border border-dashed border-slate-300">
                        Identified count is under threshold (&lt;5). Redacted to prevent re-identification.
                      </div>
                    ) : (
                      <div className="space-y-2 text-xs">
                        <div className="grid grid-cols-3 gap-2 text-center bg-slate-50 p-2.5 rounded-lg">
                          <div>
                            <div className="text-slate-400">Identified</div>
                            <div className="font-bold text-slate-800 text-sm">{cell.identified_count}</div>
                          </div>
                          <div>
                            <div className="text-slate-400">Rate / 100k</div>
                            <div className="font-bold text-slate-800 text-sm">{cell.rate_per_100k}</div>
                          </div>
                          <div>
                            <div className="text-slate-400">Peer Median</div>
                            <div className="font-bold text-slate-800 text-sm">{cell.peer_median_rate_per_100k}</div>
                          </div>
                        </div>

                        {cell.is_gap && cell.reasons.length > 0 && (
                          <div className="p-2.5 bg-red-100/60 rounded text-red-800 text-[11px] space-y-1">
                            <div className="font-semibold">Explainable Reasons:</div>
                            <div>• District rate ({cell.rate_per_100k}/100k) is below 50% of peer median ({cell.peer_median_rate_per_100k}/100k).</div>
                            <div>• Deficit: {cell.reasons[0]?.gap_deficit_per_100k} athletes per 100k below target threshold.</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Phase 2: Equipment Inventory & Overdue Loans */}
        {activeTab === 'equipment' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Equipment Management & Lending Log</h3>
                <p className="text-xs text-slate-500">
                  Append-only loans log. Overdue tracking and condition verification.
                </p>
              </div>
            </div>

            {/* Overdue Alert Banner */}
            {overdueLoans.length > 0 && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl space-y-2">
                <div className="flex items-center gap-2 text-red-800 font-semibold text-sm">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  {overdueLoans.length} Overdue Equipment Loan(s) Require Officer Follow-up
                </div>
                <div className="space-y-1 text-xs text-red-700">
                  {overdueLoans.map(l => (
                    <div key={l.id} className="flex justify-between items-center py-1 border-b border-red-200/60">
                      <span><b>{l.item_name}</b> (Borrower Ref: {l.borrower_id})</span>
                      <span className="font-medium">Due Date: {new Date(l.due_at).toLocaleDateString()}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Equipment Items Table */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-slate-600 text-xs font-semibold uppercase">
                  <tr>
                    <th className="px-6 py-3 text-left">QR Code</th>
                    <th className="px-6 py-3 text-left">Item Name</th>
                    <th className="px-6 py-3 text-left">Category</th>
                    <th className="px-6 py-3 text-left">Condition</th>
                    <th className="px-6 py-3 text-left">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white text-xs">
                  {equipmentItems.map(item => (
                    <tr key={item.id}>
                      <td className="px-6 py-3 font-mono text-slate-600">{item.qr_code}</td>
                      <td className="px-6 py-3 font-medium text-slate-900">{item.item_name}</td>
                      <td className="px-6 py-3 text-slate-600">{item.item_type}</td>
                      <td className="px-6 py-3">
                        <span className="bg-slate-100 px-2 py-0.5 rounded text-slate-700 font-medium">
                          {item.condition}
                        </span>
                      </td>
                      <td className="px-6 py-3">
                        <span className={`px-2 py-0.5 rounded font-semibold ${
                          item.status === 'AVAILABLE' ? 'bg-emerald-50 text-emerald-700' :
                          item.status === 'ISSUED' ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Unified Registry View */}
        {activeTab === 'registry' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Unified Athlete Registry</h2>
                <p className="text-xs text-slate-500">Derived Age Bands · Trigram Duplicate Checks · Minor Concealment Active</p>
              </div>
              <button
                onClick={() => { setShowOnboardModal(true); setDuplicateAlert(null); }}
                className="bg-navy-900 hover:bg-navy-800 text-amber-300 px-3 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm"
              >
                <Plus className="w-4 h-4" /> Onboard Athlete
              </button>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50 text-slate-600 text-xs font-semibold uppercase">
                  <tr>
                    <th className="px-6 py-3 text-left">KID / Ref</th>
                    <th className="px-6 py-3 text-left">Athlete Name</th>
                    <th className="px-6 py-3 text-left">Sport</th>
                    <th className="px-6 py-3 text-left">Age Band</th>
                    <th className="px-6 py-3 text-left">District</th>
                    <th className="px-6 py-3 text-left">Consent</th>
                    <th className="px-6 py-3 text-left">Status</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {athletes.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-8 text-center text-slate-400">
                        No visible records in your jurisdiction. Minor records in other districts return 404.
                      </td>
                    </tr>
                  ) : (
                    athletes.map((a) => (
                      <tr key={a.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="px-6 py-4 font-mono text-xs text-slate-600">{a.kid}</td>
                        <td className="px-6 py-4">
                          <div className="font-medium text-slate-900">{a.name}</div>
                          {a.is_minor && (
                            <span className="inline-flex items-center gap-1 text-[11px] text-red-600 font-medium">
                              <Lock className="w-3 h-3" /> Minor
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-slate-600">{a.sport_name}</td>
                        <td className="px-6 py-4">
                          <span className="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs font-medium">
                            {a.age_band}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-slate-600">{a.district_id}</td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-1 text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-medium">
                            <CheckCircle className="w-3 h-3" /> {a.consent_status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                            a.verification_status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-700' :
                            a.verification_status === 'UNDER_REVIEW' ? 'bg-amber-50 text-amber-700' :
                            a.verification_status === 'REJECTED' ? 'bg-red-50 text-red-700' : 'bg-blue-50 text-blue-700'
                          }`}>
                            {a.verification_status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => {
                                setActiveChatRecipient({
                                  id: a.contact_email || `${a.kid}@athlete.gov.in`,
                                  name: a.name,
                                  role: 'ATHLETE',
                                  athlete_id: a.id
                                });
                              }}
                              className="text-slate-600 hover:text-navy-900 border border-slate-200 hover:border-slate-300 bg-white px-2 py-1 rounded text-xs flex items-center gap-1 shadow-xs"
                              title="Direct Peer-to-Peer Chat"
                            >
                              <MessageSquare className="w-3.5 h-3.5 text-navy-700" />
                              <span>Chat</span>
                            </button>
                            <button
                              onClick={() => viewAthleteProfile(a.id)}
                              className="text-navy-900 hover:text-amber-600 font-medium text-xs flex items-center gap-1"
                            >
                              Profile <ChevronRight className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Phase 3: Schemes & Opportunities Tab */}
        {activeTab === 'schemes' && (
          <div className="space-y-6">
            {/* Header & Disclaimers */}
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-lg font-bold text-slate-900">Schemes, Rules & Opportunities Board</h2>
                <p className="text-xs text-slate-500">
                  Dual-governance rules engine with Maker-Checker sanctioning. All central/state schemes explicitly marked with advisory verification warnings.
                </p>
              </div>
              <span className="bg-amber-100 text-amber-900 border border-amber-300 text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" /> Placeholder — verify with ministry
              </span>
            </div>

            {/* Scheme Catalog */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {schemes.map((s) => (
                <div key={s.id} className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[11px] uppercase tracking-wider font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded">
                        {s.level} · {s.owner_body}
                      </span>
                      <h3 className="font-bold text-slate-900 text-base mt-1">{s.name}</h3>
                      <p className="text-xs font-mono text-slate-400">Code: {s.code}</p>
                    </div>
                    {s.verify_with_ministry && (
                      <span className="text-[10px] bg-amber-50 text-amber-800 border border-amber-200 font-semibold px-2 py-0.5 rounded">
                        Advisory Only
                      </span>
                    )}
                  </div>

                  {/* Rules list */}
                  <div className="border-t border-slate-100 pt-3 space-y-2">
                    <div className="text-xs font-bold text-slate-700 flex items-center justify-between">
                      <span>Eligibility Criteria Versions</span>
                      <span className="text-slate-400 font-normal">{s.rules.length} rule(s)</span>
                    </div>

                    {s.rules.map((r) => (
                      <div key={r.id} className="p-3 bg-slate-50 rounded-lg text-xs space-y-1.5 border border-slate-200/60">
                        <div className="flex justify-between items-center">
                          <span className="font-semibold text-slate-800">Version {r.version}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            r.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {r.status}
                          </span>
                        </div>
                        <p className="text-slate-500 text-[11px]">
                          <b>Source:</b> {r.source_document} ({r.source_clause}, {r.source_page})
                        </p>
                        <p className="text-slate-500 text-[11px]">
                          <b>Effective:</b> {r.effective_from} {r.effective_to ? `to ${r.effective_to}` : '(Ongoing)'}
                        </p>

                        {/* Maker-Checker Approval Button for Admins */}
                        {r.status === 'DRAFT' && ['NATIONAL_ADMIN', 'STATE_OFFICER'].includes(currentUser.role) && (
                          <div className="pt-2 flex justify-end">
                            <button
                              onClick={() => handleApproveRule(r.id)}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded text-xs font-semibold flex items-center gap-1 shadow-sm"
                            >
                              <CheckCircle className="w-3.5 h-3.5" /> Approve Rule (Maker-Checker)
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Athlete Eligibility Evaluator Panel */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Deterministic Athlete Eligibility Simulator</h3>
                <p className="text-xs text-slate-500">
                  Select an athlete from the registry to evaluate against active APPROVED rules. Explains criteria checks and flags missing fields.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <select
                  className="bg-white border border-slate-300 text-slate-800 text-xs rounded-lg p-2 max-w-sm"
                  value={evaluatingAthleteId || ''}
                  onChange={(e) => evaluateAthleteEligibility(e.target.value)}
                >
                  <option value="">-- Choose Athlete to Test Eligibility --</option>
                  {athletes.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.kid} · {a.sport_name} · {a.age_band})
                    </option>
                  ))}
                </select>
              </div>

              {eligibilityResults.length > 0 && (
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Evaluation Audit Results</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {eligibilityResults.map((ev, idx) => (
                      <div key={idx} className="p-4 rounded-xl border bg-slate-50/50 space-y-2 text-xs">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="font-bold text-slate-900">{ev.scheme_name}</span>
                            <p className="text-[11px] text-slate-500">Rule Version {ev.rule_version}</p>
                          </div>
                          <span className={`px-2.5 py-1 rounded-full font-bold text-[11px] ${
                            ev.eligible === true ? 'bg-emerald-100 text-emerald-800' :
                            ev.eligible === false ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {ev.eligible === true ? 'ELIGIBLE' : ev.eligible === false ? 'NOT ELIGIBLE' : 'MISSING DATA (NULL)'}
                          </span>
                        </div>

                        {ev.missing_fields && ev.missing_fields.length > 0 && (
                          <div className="p-2 bg-amber-50 rounded border border-amber-200 text-amber-800 text-[11px]">
                            <b>Missing Dossier Fields:</b> {ev.missing_fields.join(', ')}
                          </div>
                        )}

                        <div className="space-y-1">
                          <span className="text-[11px] font-semibold text-slate-700">Criteria Check Explanations:</span>
                          {ev.reasons.map((r, rIdx) => (
                            <div key={rIdx} className="flex items-center gap-1.5 text-[11px]">
                              {r.passed ? (
                                <CheckCircle className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                              ) : (
                                <AlertTriangle className="w-3.5 h-3.5 text-red-500 shrink-0" />
                              )}
                              <span className={r.passed ? 'text-slate-700' : 'text-red-700'}>{r.reason}</span>
                            </div>
                          ))}
                        </div>

                        {ev.source_refs && ev.source_refs.length > 0 && (
                          <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-200/60">
                            Source: {ev.source_refs[0].source_document} ({ev.source_refs[0].source_clause})
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Opportunities & Quota Board */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">Opportunities & Sports Quotas Board</h3>
                  <p className="text-xs text-slate-500">
                    Direct linkages to Armed Forces, Indian Railways, and PSU sports employment openings.
                  </p>
                </div>
                <span className="text-xs text-slate-500">{opportunities.length} active position(s)</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {opportunities.map((opp) => (
                  <div key={opp.id} className="p-4 border rounded-xl bg-slate-50/50 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-[11px] uppercase tracking-wider font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded">
                          {opp.type} · {opp.employer}
                        </span>
                        <h4 className="font-bold text-slate-900 text-sm mt-1">{opp.title}</h4>
                        <p className="text-xs text-slate-500">
                          Slots: <b>{opp.slots}</b> · Scope: {opp.state_scope || 'National'} · Deadline: {opp.deadline}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 pt-2 border-t border-slate-200/60">
                      {athletes.length > 0 && (
                        <button
                          onClick={() => handleApplyOpportunity(opp.id, athletes[0].id)}
                          className="bg-navy-900 hover:bg-navy-800 text-white px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                        >
                          <Briefcase className="w-3.5 h-3.5" /> Submit Dossier for {athletes[0].name}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Trainer Certifications & Expiry Tracking */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
              <div>
                <h3 className="font-bold text-slate-900 text-base">Coach & Trainer Certifications</h3>
                <p className="text-xs text-slate-500">
                  Accreditation validity registry. Revoked credentials automatically block academy placement.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {trainerCerts.map((cert) => (
                  <div key={cert.id} className="p-3 border rounded-xl bg-slate-50 text-xs space-y-1.5">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-slate-800">{cert.course}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        cert.status === 'ACTIVE' ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {cert.status}
                      </span>
                    </div>
                    <p className="text-slate-500">Provider: {cert.provider} · Issued: {cert.issued_on}</p>
                    <p className="text-slate-700 font-medium">
                      Expires: {cert.expires_on} ({cert.days_to_expiry > 0 ? `${cert.days_to_expiry} days remaining` : 'Expired'})
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Verification Workbench */}
        {activeTab === 'verification' && (
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">District Verification Workbench</h2>
              <p className="text-xs text-slate-500">Only District Officers & Admins can verify records. Coaches are prohibited from self-verifying.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {athletes.filter(a => a.verification_status !== 'VERIFIED').length === 0 ? (
                <div className="col-span-2 p-8 bg-white rounded-xl border border-slate-200 text-center text-slate-400">
                  No records currently pending verification in district {currentUser.district_id || 'ALL'}.
                </div>
              ) : (
                athletes.filter(a => a.verification_status !== 'VERIFIED').map(ath => (
                  <div key={ath.id} className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="text-xs font-mono text-slate-500">{ath.kid}</span>
                        <h3 className="font-bold text-slate-900 text-base">{ath.name}</h3>
                        <p className="text-xs text-slate-500">{ath.sport_name} · Band: {ath.age_band} · Dist: {ath.district_id}</p>
                      </div>
                      <span className="text-xs bg-amber-50 text-amber-800 font-semibold px-2 py-0.5 rounded">
                        {ath.verification_status}
                      </span>
                    </div>

                    <div className="pt-3 border-t border-slate-100 flex items-center justify-end space-x-2">
                      {ath.verification_status === 'SUBMITTED' && (
                        <button
                          onClick={() => handleVerificationAction(ath.id, 'UNDER_REVIEW', 'Officer initiated dossier review')}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1.5 rounded text-xs font-medium"
                        >
                          Begin Review
                        </button>
                      )}
                      {ath.verification_status === 'UNDER_REVIEW' && (
                        <>
                          <button
                            onClick={() => handleVerificationAction(ath.id, 'NEEDS_INFO', 'Discrepancy in school achievement proof')}
                            className="bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1.5 rounded text-xs font-medium"
                          >
                            Request Info
                          </button>
                          <button
                            onClick={() => {
                              setShowRejectModal(ath);
                              setRejectReasonInput('');
                              setRejectReportInput(`Formal Candidate Verification Audit:
Date: ${new Date().toISOString()}
Verifier: ${currentUser.full_name} (${currentUser.role})
District: ${ath.district_id}
Athlete: ${ath.name} (KID: ${ath.kid})
Findings: Criteria mismatch with primary documentation. Athlete notified with remedial directives.`);
                            }}
                            className="bg-red-50 hover:bg-red-100 text-red-700 px-2.5 py-1.5 rounded text-xs font-medium"
                          >
                            Reject Candidate
                          </button>
                          <button
                            onClick={() => handleVerificationAction(ath.id, 'VERIFIED', 'All primary documents verified by DSO')}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1.5 rounded text-xs font-medium"
                          >
                            Verify & Approve
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => {
                          setActiveChatRecipient({
                            id: ath.coach_email || 'coach@demo.gov.in',
                            name: ath.coach_name || 'Coach / Specialist',
                            role: 'COACH',
                            athlete_id: ath.id
                          });
                        }}
                        className="bg-navy-50 hover:bg-navy-100 text-navy-800 border border-navy-200 px-2.5 py-1.5 rounded text-xs font-medium flex items-center gap-1"
                        title="Chat directly with coach or athlete"
                      >
                        <MessageSquare className="w-3.5 h-3.5 text-navy-700" />
                        <span>Direct Chat</span>
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Facilities Tab */}
        {activeTab === 'facilities' && (
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Sports Facilities Inventory</h2>
              <p className="text-xs text-slate-500">PostGIS Coordinates & Scoped Jurisdictional Coverage</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {facilities.map(f => (
                <div key={f.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-xs uppercase tracking-wider font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                        {f.type}
                      </span>
                      <h3 className="font-bold text-slate-900 mt-1">{f.name}</h3>
                      <p className="text-xs text-slate-500">District: {f.district_id} · Lat/Lon: {f.latitude}, {f.longitude}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {f.sports.map(s => (
                      <span key={s} className="bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded">
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Phase 4: AI Agent & Policy RAG Tab */}
        {activeTab === 'agent' && (
          <div className="space-y-6">
            {/* Header banner */}
            <div className="bg-gradient-to-r from-navy-900 to-indigo-950 text-white rounded-2xl p-6 shadow-sm border border-navy-800 space-y-3">
              <div className="flex items-center gap-2 text-amber-400 font-bold text-base">
                <Sparkles className="w-5 h-5" /> TrackNet Grounded AI Decision-Support Agent
              </div>
              <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
                Empowered with <b>100% Citation Enforcement</b> over verified government sports guidelines and circulars. 
                Strictly read-only execution by default; state mutations emit non-autonomous <b>Action Proposals</b> requiring explicit officer approval tokens.
              </p>
              <div className="flex flex-wrap gap-2 pt-1 text-xs">
                <span className="bg-navy-800/90 text-slate-300 px-3 py-1 rounded-full border border-navy-700">
                  Role: <b>{currentUser.role}</b> ({currentUser.district_id || currentUser.state_id || 'ALL INDIA'})
                </span>
                <span className="bg-emerald-950/80 text-emerald-300 px-3 py-1 rounded-full border border-emerald-800">
                  RBAC Boundary: Scoped
                </span>
                <span className="bg-amber-950/80 text-amber-300 px-3 py-1 rounded-full border border-amber-800">
                  Autonomous Mutations: Blocked
                </span>
              </div>
            </div>

            {/* Quick Prompt Starters */}
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="text-slate-500 font-semibold self-center">Prompt Starters:</span>
              <button
                onClick={() => setAgentPrompt("What are the talent identification benchmarks and verification requirements?")}
                className="bg-white hover:bg-slate-50 border text-slate-700 px-2.5 py-1 rounded-lg shadow-2xs"
              >
                Talent ID Benchmarks (MYAS Guidelines)
              </button>
              <button
                onClick={() => setAgentPrompt("Check pipeline bottlenecks and identify sport gap cells exceeding peer median")}
                className="bg-white hover:bg-slate-50 border text-slate-700 px-2.5 py-1 rounded-lg shadow-2xs"
              >
                Pipeline Gap Diagnosis
              </button>
              <button
                onClick={() => setAgentPrompt("List overdue equipment loans requiring officer inspection")}
                className="bg-white hover:bg-slate-50 border text-slate-700 px-2.5 py-1 rounded-lg shadow-2xs"
              >
                Overdue Equipment Audit
              </button>
              <button
                onClick={() => setAgentPrompt("Verify athlete Aarav Patil based on State Youth Boxing Championship gold medal")}
                className="bg-white hover:bg-slate-50 border text-slate-700 px-2.5 py-1 rounded-lg shadow-2xs"
              >
                Draft Athlete Verification Proposal
              </button>
            </div>

            {/* Agent Query Input Form */}
            <form onSubmit={handleAgentQuery} className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm space-y-3">
              <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider">
                Ask Grounded Assistant (Policy RAG & Scoped Tools)
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={agentPrompt}
                  onChange={(e) => setAgentPrompt(e.target.value)}
                  placeholder="e.g. Inquire about Khelo India age norms, DPDP minor privacy, or draft an athlete action proposal..."
                  className="flex-1 border rounded-lg p-2.5 text-xs outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400"
                />
                <button
                  type="submit"
                  disabled={isAgentLoading}
                  className="bg-navy-900 hover:bg-navy-800 disabled:opacity-50 text-white px-5 py-2.5 rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm"
                >
                  <Bot className="w-4 h-4" />
                  {isAgentLoading ? 'Consulting Guidelines...' : 'Ask Assistant'}
                </button>
              </div>
            </form>

            {/* Agent Response Card */}
            {agentResponse && (
              <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-sm space-y-5">
                <div className="flex justify-between items-center border-b pb-3">
                  <div className="flex items-center gap-2">
                    <Bot className="w-5 h-5 text-indigo-600" />
                    <span className="font-bold text-slate-900 text-sm">Grounded Decision-Support Answer</span>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                    agentResponse.confidence_level === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                    agentResponse.confidence_level === 'MEDIUM' ? 'bg-blue-100 text-blue-800' : 'bg-amber-100 text-amber-800'
                  }`}>
                    {agentResponse.confidence_level} Confidence
                  </span>
                </div>

                {/* Synthesis Text */}
                <div className="p-4 bg-slate-50 rounded-xl text-xs text-slate-800 leading-relaxed border border-slate-200/60 font-medium">
                  {agentResponse.response_text}
                </div>

                {/* Policy Citations (100% Citation Enforcement) */}
                {agentResponse.citations && agentResponse.citations.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5 text-amber-600" /> Verified Primary Source Citations ({agentResponse.citations.length})
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {agentResponse.citations.map((c: any, idx: number) => (
                        <div key={idx} className="p-3 bg-amber-50/60 border border-amber-200 rounded-lg text-xs space-y-1">
                          <div className="font-bold text-amber-900">{c.title}</div>
                          <div className="text-[11px] text-amber-800 font-mono">
                            {c.source_document} · {c.source_clause}, {c.source_page}
                          </div>
                          <p className="text-[11px] text-slate-600 italic">"{c.text_content}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tool Calling Execution Trace */}
                {agentResponse.tool_calls_executed && agentResponse.tool_calls_executed.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                      <Activity className="w-3.5 h-3.5 text-blue-600" /> Read-Only Tool Executions ({agentResponse.tool_calls_executed.length})
                    </span>
                    <div className="space-y-2">
                      {agentResponse.tool_calls_executed.map((tc: any, idx: number) => (
                        <div key={idx} className="p-2.5 bg-slate-100 rounded-lg font-mono text-[11px] text-slate-700 flex justify-between items-center">
                          <span><b>Tool:</b> {tc.tool}</span>
                          <span className="text-slate-500">Output: {JSON.stringify(tc.result).slice(0, 80)}...</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Proposed Actions (Maker-Checker Approval Token) */}
                {agentResponse.proposed_actions && agentResponse.proposed_actions.length > 0 && (
                  <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl space-y-3">
                    <div className="flex items-center gap-1.5 text-purple-900 font-bold text-xs">
                      <Lock className="w-4 h-4 text-purple-700" /> Non-Autonomous Action Proposal Generated
                    </div>
                    <p className="text-xs text-purple-800">
                      The agent proposed a mutation. Per system safety rules, state changes are blocked without human officer sanction.
                    </p>
                    {agentResponse.proposed_actions.map((pa: any) => (
                      <div key={pa.proposal_id} className="bg-white p-3 rounded-lg border border-purple-200 flex justify-between items-center text-xs">
                        <div>
                          <span className="font-bold text-slate-900">{pa.action_type}</span>
                          <p className="text-[11px] font-mono text-slate-500">Token: {pa.approval_token}</p>
                        </div>
                        <button
                          onClick={() => handleExecuteProposal(pa.proposal_id, pa.approval_token)}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded text-xs font-bold flex items-center gap-1 shadow-sm"
                        >
                          <CheckCircle className="w-3.5 h-3.5" /> Officer Sanction & Execute
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <div className="pt-2 border-t text-[10px] text-slate-400 flex justify-between">
                  <span>Cryptographic Audit Proof: {agentResponse.audit_hash}</span>
                  <span>Model: TrackNet-Assistant-v1 (Zero PII Logging)</span>
                </div>
              </div>
            )}

            {/* Action Proposals Backlog & Audit Queue */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">Human Officer Action Proposals Backlog</h3>
                  <p className="text-xs text-slate-500">
                    Transparent queue of mutations drafted by assistant. Requires explicit approval token to execute.
                  </p>
                </div>
                <span className="text-xs font-bold text-slate-500">{agentProposals.length} proposal(s)</span>
              </div>

              {agentProposals.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  No active action proposals pending officer review.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {agentProposals.map((prop) => (
                    <div key={prop.id} className="p-4 border rounded-xl bg-slate-50/50 space-y-2 text-xs">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="font-bold text-slate-900">{prop.action_type}</span>
                          <p className="text-[11px] text-slate-500">Target: {prop.target_entity} · ID: {prop.target_id}</p>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          prop.status === 'EXECUTED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                        }`}>
                          {prop.status}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600"><b>Reason:</b> {prop.reasoning}</p>
                      <div className="font-mono text-[10px] text-slate-400">Token: {prop.approval_token}</div>

                      {prop.status !== 'EXECUTED' && (
                        <div className="pt-2 flex justify-end">
                          <button
                            onClick={() => handleExecuteProposal(prop.id, prop.approval_token)}
                            className="bg-navy-900 hover:bg-navy-800 text-white px-3 py-1 rounded text-xs font-semibold flex items-center gap-1 shadow-sm"
                          >
                            <CheckCircle className="w-3.5 h-3.5" /> Authorize Proposal
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Phase 5: State Adapters & Offline PWA Protocol */}
        {activeTab === 'adapters' && (
          <div className="space-y-6">
            {/* Header / Sub-Nav with State Switcher */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <Globe className="w-5 h-5 text-cyan-600" />
                  State Federation Adapter & Offline Protocol
                </h3>
                <p className="text-xs text-slate-500">
                  Federated schemas, priority sports matrix, and resilient offline-first field synchronization.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg text-xs">
                  <span className="text-slate-500 font-semibold px-2">Active Adapter:</span>
                  <button
                    onClick={() => handleLoadStateManifest('MH')}
                    className={`px-3 py-1 rounded font-bold transition-all ${
                      selectedStateId === 'MH' ? 'bg-navy-900 text-amber-300 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Maharashtra (MH)
                  </button>
                  <button
                    onClick={() => handleLoadStateManifest('HR')}
                    className={`px-3 py-1 rounded font-bold transition-all ${
                      selectedStateId === 'HR' ? 'bg-navy-900 text-amber-300 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Haryana (HR)
                  </button>
                </div>
              </div>
            </div>

            {/* Offline PWA Dispatcher & In-Flight Sync Buffer */}
            <div className="bg-gradient-to-r from-slate-900 to-navy-900 rounded-xl p-5 text-white shadow-md space-y-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  {isOfflineMode ? (
                    <span className="p-2 bg-amber-500/20 text-amber-300 rounded-lg">
                      <WifiOff className="w-5 h-5 animate-pulse" />
                    </span>
                  ) : (
                    <span className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg">
                      <Wifi className="w-5 h-5" />
                    </span>
                  )}
                  <div>
                    <h4 className="font-bold text-sm">
                      {isOfflineMode ? 'PWA Offline Field Mode Active' : 'Connected to National Registry Server'}
                    </h4>
                    <p className="text-[11px] text-slate-300">
                      {isOfflineMode 
                        ? 'Mutations are queued in local IndexedDB storage until network connectivity is restored.'
                        : 'Immediate transaction mode. Enqueued mutations can be batch synced on demand.'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleSyncOfflineBatch}
                    disabled={isSyncing || offlineQueue.length === 0}
                    className="bg-amber-400 hover:bg-amber-300 disabled:opacity-40 text-navy-950 font-bold px-4 py-2 rounded-lg text-xs flex items-center gap-1.5 shadow-sm transition-all"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
                    {isSyncing ? 'Resolving Batch...' : `Sync Offline Batch (${offlineQueue.length})`}
                  </button>
                </div>
              </div>

              {/* Sync Outcome Banner */}
              {syncOutcome && (
                <div className="p-3 bg-navy-800/90 border border-navy-700 rounded-lg text-xs flex items-center justify-between text-slate-200">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span><b>Sync Completed:</b></span>
                    <span className="text-emerald-400 font-semibold">{syncOutcome.applied} Applied</span>
                    <span>·</span>
                    <span className="text-amber-400 font-semibold">{syncOutcome.server_won} Conflicts (Server Won)</span>
                    <span>·</span>
                    <span className="text-red-400 font-semibold">{syncOutcome.errors} Errors</span>
                  </div>
                  <button onClick={() => setSyncOutcome(null)} className="text-slate-400 hover:text-white">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}

              {/* Interactive Queue Enqueuer */}
              <div className="bg-navy-800/60 p-3 rounded-lg border border-navy-700/80">
                <div className="text-[11px] font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                  <Plus className="w-3.5 h-3.5 text-amber-400" />
                  Simulate Field Officer Offline Edit:
                </div>
                <div className="flex flex-wrap gap-2 text-xs">
                  {athletes.slice(0, 3).map(ath => (
                    <div key={ath.id} className="flex items-center gap-1 bg-navy-900/90 px-2 py-1 rounded border border-navy-700">
                      <span className="text-slate-200 font-medium">{ath.name}:</span>
                      <button
                        onClick={() => handleQueueOfflineMutation(ath, 'guardian_ref', 'Updated Contact in Field (LWW)')}
                        className="text-amber-300 hover:text-amber-200 text-[10px] bg-navy-800 px-1.5 py-0.5 rounded border border-navy-600"
                        title="Contact update should succeed via Last-Write-Wins"
                      >
                        Edit Contact (LWW)
                      </button>
                      <button
                        onClick={() => handleQueueOfflineMutation(ath, 'verification_status', 'VERIFIED')}
                        className="text-red-300 hover:text-red-200 text-[10px] bg-navy-800 px-1.5 py-0.5 rounded border border-navy-600"
                        title="Tampering verification status will be rejected by server-wins policy"
                      >
                        Force Verify (Server Wins)
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pending Offline Mutations Table */}
              {offlineQueue.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-navy-800">
                  <div className="text-xs font-semibold text-amber-300">Pending Field Queue:</div>
                  <div className="max-h-36 overflow-y-auto space-y-1 text-xs">
                    {offlineQueue.map(item => (
                      <div key={item.id} className="flex justify-between items-center bg-navy-800/80 px-3 py-1.5 rounded text-[11px]">
                        <div>
                          <span className="font-bold text-white">{item.athlete_name}</span>
                          <span className="text-slate-400 ml-2">Field: <code className="text-cyan-300">{item.field_name}</code></span>
                          <span className="text-slate-400 ml-2">Value: <span className="text-amber-200">"{String(item.field_value)}"</span></span>
                        </div>
                        <span className="text-slate-400 font-mono text-[10px]">Queued: {new Date(item.queued_at).toLocaleTimeString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* State Manifest Details */}
            {selectedStateManifest && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Priority Sports Matrix */}
                <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                        <Award className="w-4 h-4 text-amber-500" />
                        State Priority Sports Matrix ({selectedStateManifest.state_name})
                      </h4>
                      <p className="text-[11px] text-slate-500">
                        Tailored sports allocation, talent density goals, and target age bands.
                      </p>
                    </div>
                    <span className="bg-cyan-50 text-cyan-800 font-mono text-xs px-2 py-0.5 rounded font-bold">
                      v{selectedStateManifest.version}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {selectedStateManifest.priority_sports.map((ps, idx) => (
                      <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center text-xs">
                        <div>
                          <div className="font-bold text-slate-800 flex items-center gap-2">
                            <span>{ps.name}</span>
                            <span className="text-[10px] font-mono bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded">
                              {ps.sport_code}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-500 mt-0.5">Target Age: {ps.target_age_group}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-bold text-navy-900">
                            {ps.talent_density_target} / 100k
                          </div>
                          <div className="text-[10px] text-slate-400">Target Density</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="pt-2 border-t text-[11px] text-slate-500 flex items-center gap-2">
                    <Globe className="w-3.5 h-3.5 text-slate-400" />
                    <span>Regional Languages Supported: <b>{selectedStateManifest.regional_languages.join(', ')}</b></span>
                  </div>
                </div>

                {/* Local Statutory Policy Overrides */}
                <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <BookOpen className="w-4 h-4 text-blue-600" />
                      Statutory Policy Rules ({selectedStateManifest.state_name})
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      State-specific legal frameworks and sports incentive schemes.
                    </p>
                  </div>

                  <div className="space-y-3">
                    {selectedStateManifest.local_policy_overrides.map((pol, idx) => (
                      <div key={idx} className="p-3 bg-blue-50/50 rounded-lg border border-blue-100 text-xs space-y-1">
                        <div className="font-bold text-blue-950 flex justify-between">
                          <span>{pol.label}</span>
                          <span className="font-mono text-[10px] text-blue-700 bg-blue-100 px-1.5 py-0.2 rounded">
                            {pol.key}
                          </span>
                        </div>
                        <p className="text-slate-700 text-[11px]">{pol.value}</p>
                        <div className="font-mono text-[10px] text-slate-500">
                          Ref: {pol.statutory_reference}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Server Sync Log & Audit Records */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-slate-500" />
                    Server Sync History & Conflict Audit Log
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    Deterministic conflict resolution log: Server-wins on verification state; LWW on contacts.
                  </p>
                </div>
                <span className="text-xs font-bold text-slate-500">{syncHistory.length} sync record(s)</span>
              </div>

              {syncHistory.length === 0 ? (
                <div className="p-6 text-center text-slate-400 text-xs">
                  No sync batches processed yet.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b bg-slate-50 text-slate-600 font-semibold">
                        <th className="py-2 px-3">Mutation ID</th>
                        <th className="py-2 px-3">Field</th>
                        <th className="py-2 px-3">Resolution Status</th>
                        <th className="py-2 px-3">Device ID</th>
                        <th className="py-2 px-3">Synced At</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {syncHistory.slice(0, 8).map((rec: any) => (
                        <tr key={rec.id} className="hover:bg-slate-50">
                          <td className="py-2 px-3 font-mono text-[11px] text-slate-600">{rec.client_mutation_id}</td>
                          <td className="py-2 px-3 font-semibold text-slate-800">{rec.field_name}</td>
                          <td className="py-2 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              rec.sync_status === 'APPLIED' 
                                ? 'bg-emerald-100 text-emerald-800' 
                                : rec.sync_status === 'CONFLICT_SERVER_WON' 
                                ? 'bg-amber-100 text-amber-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {rec.sync_status}
                            </span>
                            {rec.conflict_reason && (
                              <div className="text-[10px] text-slate-500 mt-0.5">{rec.conflict_reason}</div>
                            )}
                          </td>
                          <td className="py-2 px-3 text-slate-500 text-[11px]">{rec.client_device_id}</td>
                          <td className="py-2 px-3 text-slate-400 text-[11px]">
                            {new Date(rec.synced_at).toLocaleTimeString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Phase 6: Pilot Hardening, Security ASVS & Resilience */}
        {activeTab === 'security' && (
          <div className="space-y-6">
            {/* Security Top Banner */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-emerald-600" />
                  Pilot Hardening, ASVS L2 & Resilience Center
                </h3>
                <p className="text-xs text-slate-500">
                  Continuous cryptographic hash verification, AI emergency kill-switch, DPDP Act erasure, and automated disaster drills.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleVerifyAuditChain}
                  className="bg-navy-900 hover:bg-navy-800 text-amber-300 px-3.5 py-2 rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm transition-all"
                >
                  <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
                  Verify Hash Chain
                </button>
                <button
                  onClick={handleRunChaosDrill}
                  disabled={isDrillRunning}
                  className="bg-purple-700 hover:bg-purple-800 text-white px-3.5 py-2 rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-sm transition-all disabled:opacity-50"
                >
                  <Terminal className={`w-3.5 h-3.5 ${isDrillRunning ? 'animate-spin' : ''}`} />
                  {isDrillRunning ? 'Executing Drill...' : 'Run Chaos Drill'}
                </button>
              </div>
            </div>

            {erasureFeedback && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs flex justify-between items-center">
                <span><b>Statutory Erasure Complete:</b> {erasureFeedback}</span>
                <button onClick={() => setErasureFeedback(null)} className="text-emerald-700 hover:text-emerald-950">
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* Grid 1: Cryptographic Audit Hash Chain + Emergency Kill-Switch */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Audit Hash Chain Card */}
              <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <Lock className="w-4 h-4 text-emerald-600" />
                      Tamper-Evident SHA-256 Audit Chain
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      Zero-tampering cryptographic link between sequential system mutations.
                    </p>
                  </div>
                  {auditChainStatus && (
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      auditChainStatus.is_valid ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {auditChainStatus.is_valid ? 'INTEACT & VERIFIED' : 'TAMPER DETECTED'}
                    </span>
                  )}
                </div>

                {auditChainStatus ? (
                  <div className="space-y-3 text-xs">
                    <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
                      <div>
                        <div className="text-[10px] text-slate-400">Total Audit Blocks</div>
                        <div className="text-base font-bold text-slate-800">{auditChainStatus.total_records}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-slate-400">Cryptographically Valid</div>
                        <div className="text-base font-bold text-emerald-600">{auditChainStatus.verified_records}</div>
                      </div>
                    </div>

                    <div className="space-y-1.5">
                      <div className="text-[11px] font-semibold text-slate-600">Genesis Block Hash:</div>
                      <div className="font-mono text-[10px] bg-slate-100 p-2 rounded truncate text-slate-700">
                        {auditChainStatus.genesis_hash}
                      </div>
                      <div className="text-[11px] font-semibold text-slate-600">Chain Tip Hash:</div>
                      <div className="font-mono text-[10px] bg-slate-100 p-2 rounded truncate text-slate-700">
                        {auditChainStatus.tip_hash}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 text-center text-slate-400 text-xs">
                    Click "Verify Hash Chain" to execute complete SHA-256 proof.
                  </div>
                )}
              </div>

              {/* Emergency Agent Kill-Switch */}
              <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <ShieldAlert className="w-4 h-4 text-red-600" />
                      AI Agent Emergency Kill-Switch
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      Instantly cut off all generative RAG queries and mutation proposals.
                    </p>
                  </div>
                  {killSwitchStatus && (
                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      killSwitchStatus.is_globally_disabled ? 'bg-red-100 text-red-800 animate-pulse' : 'bg-emerald-100 text-emerald-800'
                    }`}>
                      {killSwitchStatus.is_globally_disabled ? 'AGENT DISABLED' : 'OPERATIONAL'}
                    </span>
                  )}
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                    <div className="text-[11px] text-slate-500 font-medium">Kill-Switch Reason / State:</div>
                    <div className="text-slate-800 font-semibold">{killSwitchStatus?.reason || 'Normal operational state'}</div>
                    <div className="text-[10px] text-slate-400">
                      Updated By: {killSwitchStatus?.updated_by || 'system'} · {killSwitchStatus ? new Date(killSwitchStatus.updated_at).toLocaleTimeString() : ''}
                    </div>
                  </div>

                  <div className="pt-2 flex gap-3">
                    {killSwitchStatus?.is_globally_disabled ? (
                      <button
                        onClick={() => handleToggleKillSwitch(false)}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded-lg text-xs shadow-sm transition-all"
                      >
                        Restore Agent Operations
                      </button>
                    ) : (
                      <button
                        onClick={() => handleToggleKillSwitch(true)}
                        className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold py-2 rounded-lg text-xs shadow-sm transition-all flex items-center justify-center gap-1.5"
                      >
                        <ShieldAlert className="w-4 h-4" />
                        Activate Emergency Kill-Switch
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Chaos Resilience Drill Report */}
            {chaosDrillOutput && (
              <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
                <div className="flex justify-between items-center border-b pb-3">
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                      <Terminal className="w-4 h-4 text-purple-600" />
                      Automated Chaos Drill Output ({chaosDrillOutput.drill_id})
                    </h4>
                    <p className="text-[11px] text-slate-500">
                      Self-healing, database connectivity, and AES encryption loop testing.
                    </p>
                  </div>
                  <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                    chaosDrillOutput.passed ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {chaosDrillOutput.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  {chaosDrillOutput.checks.map((c: any, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                      <div className="font-bold text-slate-800 flex justify-between">
                        <span>{c.check}</span>
                        <span className="text-[10px] text-emerald-600 font-bold">{c.status}</span>
                      </div>
                      <p className="text-[11px] text-slate-600">{c.details}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* DPDP Act Right-to-be-Forgotten / Data Erasure Table */}
            <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <div>
                  <h4 className="font-bold text-slate-900 text-sm flex items-center gap-1.5">
                    <Trash2 className="w-4 h-4 text-red-600" />
                    DPDP Act 2023 Statutory Data Erasure (Right-to-be-Forgotten)
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    Statutory erasure workflow for withdrawn consent: permanently redacts PII and updates status to DELETED.
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b bg-slate-50 text-slate-600 font-semibold">
                      <th className="py-2 px-3">Athlete</th>
                      <th className="py-2 px-3">KID</th>
                      <th className="py-2 px-3">Status</th>
                      <th className="py-2 px-3">Consent</th>
                      <th className="py-2 px-3 text-right">Statutory Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {athletes.map(ath => (
                      <tr key={ath.id} className="hover:bg-slate-50">
                        <td className="py-2 px-3 font-semibold text-slate-900">{ath.name}</td>
                        <td className="py-2 px-3 font-mono text-[11px] text-slate-500">{ath.kid}</td>
                        <td className="py-2 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            ath.verification_status === 'DELETED' ? 'bg-red-100 text-red-800' : 'bg-slate-100 text-slate-700'
                          }`}>
                            {ath.verification_status}
                          </span>
                        </td>
                        <td className="py-2 px-3 text-slate-600 text-[11px]">{ath.consent_status}</td>
                        <td className="py-2 px-3 text-right">
                          {ath.verification_status !== 'DELETED' ? (
                            <button
                              onClick={() => handleExecuteDPDPErasure(ath.id)}
                              className="bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 px-2.5 py-1 rounded text-[11px] font-bold flex items-center gap-1 ml-auto shadow-2xs"
                            >
                              <Trash2 className="w-3 h-3 text-red-600" />
                              Execute Erasure
                            </button>
                          ) : (
                            <span className="text-slate-400 italic text-[11px]">PII Redacted</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Onboarding Modal */}
      {showOnboardModal && (
        <div className="fixed inset-0 bg-navy-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="font-bold text-lg text-slate-900">Onboard Athlete to Registry</h3>
              <button onClick={() => setShowOnboardModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {duplicateAlert?.is_duplicate && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-2">
                <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Potential Duplicate Detected ({duplicateAlert.candidates[0].confidence_score * 100}% Confidence)
                </div>
                <p className="text-xs text-amber-700">
                  Matches existing athlete: <b>{duplicateAlert.candidates[0].name}</b> ({duplicateAlert.candidates[0].kid}). 
                  Auto-merge is disabled. Confirm below if this is verified to be a different individual.
                </p>
              </div>
            )}

            <form onSubmit={checkDuplicateAndSubmit} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700">Full Name</label>
                <input
                  type="text"
                  required
                  value={onboardForm.name}
                  onChange={(e) => setOnboardForm({ ...onboardForm, name: e.target.value })}
                  placeholder="e.g. Aarav Shinde"
                  className="w-full mt-1 p-2 border rounded-lg"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700">Date of Birth</label>
                  <input
                    type="date"
                    required
                    value={onboardForm.dob}
                    onChange={(e) => setOnboardForm({ ...onboardForm, dob: e.target.value })}
                    className="w-full mt-1 p-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700">Gender</label>
                  <select
                    value={onboardForm.gender}
                    onChange={(e) => setOnboardForm({ ...onboardForm, gender: e.target.value })}
                    className="w-full mt-1 p-2 border rounded-lg"
                  >
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700">Primary Sport</label>
                <select
                  value={onboardForm.sport_code}
                  onChange={(e) => setOnboardForm({ ...onboardForm, sport_code: e.target.value })}
                  className="w-full mt-1 p-2 border rounded-lg"
                >
                  <option value="BOX">Boxing</option>
                  <option value="WRE">Wrestling</option>
                  <option value="ATH">Athletics</option>
                  <option value="KAB">Kabaddi</option>
                  <option value="BAD">Badminton</option>
                </select>
              </div>

              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl space-y-2">
                <div className="font-semibold text-blue-900 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5" /> Minor Privacy & Guardian Consent (DPDP Act)
                </div>
                <div>
                  <label className="text-slate-600">Guardian Name & Relation</label>
                  <input
                    type="text"
                    required
                    value={onboardForm.guardian_ref}
                    onChange={(e) => setOnboardForm({ ...onboardForm, guardian_ref: e.target.value })}
                    className="w-full mt-1 p-1.5 border rounded-lg text-xs"
                  />
                </div>
                <label className="flex items-center gap-2 cursor-pointer pt-1">
                  <input
                    type="checkbox"
                    checked={onboardForm.consent_status === 'GRANTED'}
                    onChange={(e) => setOnboardForm({ ...onboardForm, consent_status: e.target.checked ? 'GRANTED' : 'PENDING' })}
                    className="rounded text-navy-900"
                  />
                  <span className="text-slate-700 font-medium text-[11px]">Verifiable Guardian Consent Form Signed and Filed</span>
                </label>
              </div>

              <div className="pt-3 border-t flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowOnboardModal(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-slate-50 text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-navy-900 hover:bg-navy-800 text-amber-300 font-semibold rounded-lg"
                >
                  {duplicateAlert?.is_duplicate ? "Confirm Different Person & Submit" : "Verify & Submit"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Athlete Profile Modal */}
      {selectedAthlete && (
        <div className="fixed inset-0 bg-navy-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start border-b pb-3">
              <div>
                <span className="font-mono text-xs text-slate-500">{selectedAthlete.kid}</span>
                <h3 className="font-bold text-xl text-slate-900 flex items-center gap-2">
                  {selectedAthlete.name}
                  {selectedAthlete.is_minor && (
                    <span className="text-xs bg-red-50 text-red-700 px-2 py-0.5 rounded font-normal flex items-center gap-1">
                      <Lock className="w-3 h-3" /> Minor Restricted
                    </span>
                  )}
                </h3>
                <p className="text-xs text-slate-500">{selectedAthlete.sport_name} · Band: {selectedAthlete.age_band} · {selectedAthlete.district_id}</p>
              </div>
              <button onClick={() => setSelectedAthlete(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Rejection Audit Details Banner */}
            {selectedAthlete.verification_status === 'REJECTED' && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-xl space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-red-900 flex items-center gap-1.5 text-sm">
                    <AlertTriangle className="w-4 h-4 text-red-600" /> Candidate Verification Rejected
                  </span>
                  <span className="bg-red-200 text-red-800 font-semibold px-2 py-0.5 rounded text-[11px]">
                    Status: REJECTED
                  </span>
                </div>
                <div className="text-slate-700">
                  <span className="font-semibold text-slate-900">Rejected By:</span> {selectedAthlete.rejected_by || 'Designated District Sports Officer'}
                </div>
                <div className="text-slate-700">
                  <span className="font-semibold text-slate-900">Reason:</span> {selectedAthlete.rejection_reason || 'Discrepancy in documentation or criteria failure'}
                </div>
                {selectedAthlete.rejection_report && (
                  <div className="mt-2 pt-2 border-t border-red-200">
                    <span className="font-semibold text-red-900 flex items-center gap-1 mb-1">
                      <FileText className="w-3.5 h-3.5" /> Official Verification & Audit Report
                    </span>
                    <pre className="bg-white p-2.5 rounded border border-red-200 text-[11px] font-mono text-slate-700 whitespace-pre-wrap">
                      {selectedAthlete.rejection_report}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Profile Status & Services / Needs Matrix */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs">
              <div>
                <span className="font-bold text-slate-900 flex items-center gap-1 mb-1 text-slate-800">
                  <Sparkles className="w-3.5 h-3.5 text-amber-500" /> Support Demands & Needs
                </span>
                <p className="text-[11px] text-slate-500 mb-1.5">What the player requires for development:</p>
                <div className="flex flex-wrap gap-1">
                  {(selectedAthlete.support_demands || ['Equipment sponsorship', 'High-altitude training']).map((dem, idx) => (
                    <span key={idx} className="bg-amber-100 text-amber-900 px-2 py-0.5 rounded-full font-medium text-[11px]">
                      {dem}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <span className="font-bold text-slate-900 flex items-center gap-1 mb-1 text-slate-800">
                  <Briefcase className="w-3.5 h-3.5 text-blue-500" /> Services Offered & Specialization
                </span>
                <p className="text-[11px] text-slate-500 mb-1.5">Contribution & mutual assistance:</p>
                <div className="flex flex-wrap gap-1">
                  {(selectedAthlete.services_offered || ['Sparring partner', 'Junior clinic demo']).map((off, idx) => (
                    <span key={idx} className="bg-blue-100 text-blue-900 px-2 py-0.5 rounded-full font-medium text-[11px]">
                      {off}
                    </span>
                  ))}
                </div>
              </div>
              <div className="col-span-1 md:col-span-2 pt-2 border-t border-slate-200 flex justify-between items-center">
                <div className="text-[11px] text-slate-600">
                  <span className="font-semibold">Specialist Care Ref:</span> {selectedAthlete.specialist_contact_ref || 'SAI Sports Medicine Centre, Pune'}
                </div>
                <button
                  onClick={() => setActiveMappingEditAthlete(selectedAthlete)}
                  className="text-xs bg-white border border-slate-300 hover:bg-slate-100 text-slate-700 px-2.5 py-1 rounded font-medium shadow-sm"
                >
                  Edit Demands & Services
                </button>
              </div>
            </div>

            {/* Mutual Mapping: Player, Coach, Trainer & Specialist Contacts */}
            <div className="space-y-2 pt-2 border-t">
              <h4 className="font-semibold text-slate-800 text-sm flex items-center gap-1.5">
                <Users className="w-4 h-4 text-emerald-600" /> Mapped Team & Contact Roster
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {/* Athlete Direct Contact Card */}
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5">
                  <div className="font-semibold text-slate-900 flex items-center justify-between">
                    <span>Athlete Contact</span>
                    <button
                      onClick={() => {
                        setActiveChatRecipient({
                          id: selectedAthlete.contact_email || `${selectedAthlete.kid}@athlete.gov.in`,
                          name: selectedAthlete.name,
                          role: 'ATHLETE',
                          athlete_id: selectedAthlete.id
                        });
                      }}
                      className="text-navy-900 hover:text-amber-600 font-medium flex items-center gap-1 text-[11px] bg-white border px-1.5 py-0.5 rounded shadow-xs"
                    >
                      <MessageSquare className="w-3 h-3 text-navy-700" /> Chat
                    </button>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <Phone className="w-3 h-3 text-slate-400" />
                    <span>{selectedAthlete.contact_phone || '+91-98200-XXXXX'}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <Mail className="w-3 h-3 text-slate-400" />
                    <span>{selectedAthlete.contact_email || `${selectedAthlete.kid}@athlete.gov.in`}</span>
                  </div>
                </div>

                {/* Assigned Coach Contact Card */}
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5">
                  <div className="font-semibold text-slate-900 flex items-center justify-between">
                    <span>Assigned Coach: {selectedAthlete.coach_name || 'Coach Sharma'}</span>
                    <button
                      onClick={() => {
                        setActiveChatRecipient({
                          id: selectedAthlete.coach_email || 'coach@demo.gov.in',
                          name: selectedAthlete.coach_name || 'Coach Sharma',
                          role: 'COACH',
                          athlete_id: selectedAthlete.id
                        });
                      }}
                      className="text-navy-900 hover:text-amber-600 font-medium flex items-center gap-1 text-[11px] bg-white border px-1.5 py-0.5 rounded shadow-xs"
                    >
                      <MessageSquare className="w-3 h-3 text-navy-700" /> Chat
                    </button>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <Phone className="w-3 h-3 text-slate-400" />
                    <span>{selectedAthlete.coach_phone || '+91-98111-XXXXX'}</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <Mail className="w-3 h-3 text-slate-400" />
                    <span>{selectedAthlete.coach_email || 'coach@sportsauthority.gov.in'}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t">
              <h4 className="font-semibold text-slate-800 text-sm flex items-center gap-1.5">
                <Award className="w-4 h-4 text-amber-500" /> Verified Achievements
              </h4>
              {selectedAthlete.achievements && selectedAthlete.achievements.length > 0 ? (
                <div className="space-y-2">
                  {selectedAthlete.achievements.map(ach => (
                    <div key={ach.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex justify-between items-center text-xs">
                      <div>
                        <div className="font-semibold text-slate-800">{ach.event}</div>
                        <div className="text-slate-500 capitalize">{ach.level} Level · {ach.event_date}</div>
                      </div>
                      <span className="bg-amber-100 text-amber-900 font-bold px-2 py-1 rounded">
                        {ach.result}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No achievements recorded yet.</p>
              )}
            </div>

            <div className="space-y-2 pt-2 border-t">
              <h4 className="font-semibold text-slate-800 text-sm flex items-center gap-1.5">
                <Clock className="w-4 h-4 text-blue-500" /> Athlete Journey Timeline (Append-Only)
              </h4>
              {selectedAthlete.journey_events && selectedAthlete.journey_events.length > 0 ? (
                <div className="relative pl-4 border-l-2 border-slate-200 space-y-4 my-2 text-xs">
                  {selectedAthlete.journey_events.map(ev => (
                    <div key={ev.id} className="relative">
                      <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 bg-blue-600 rounded-full" />
                      <div className="font-semibold uppercase tracking-wider text-slate-700 text-[11px]">{ev.event_type} · {ev.event_date}</div>
                      <div className="text-slate-600 mt-0.5">{ev.notes}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400">No journey events logged.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Rejection Modal with Audit Report Input */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-navy-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-start border-b pb-3">
              <div>
                <h3 className="font-bold text-lg text-red-900 flex items-center gap-1.5">
                  <AlertTriangle className="w-5 h-5 text-red-600" /> Reject Candidate Verification
                </h3>
                <p className="text-xs text-slate-500">
                  Athlete: <span className="font-semibold text-slate-800">{showRejectModal.name}</span> ({showRejectModal.kid})
                </p>
              </div>
              <button onClick={() => setShowRejectModal(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRejectAthlete} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Primary Rejection Reason <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Criteria mismatch in age certificate or achievement proof"
                  value={rejectReasonInput}
                  onChange={(e) => setRejectReasonInput(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-red-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1 flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5 text-slate-500" /> Comprehensive Audit & Verification Report
                </label>
                <textarea
                  rows={4}
                  value={rejectReportInput}
                  onChange={(e) => setRejectReportInput(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg outline-none focus:border-red-500 font-mono text-[11px]"
                  placeholder="Detailed inspection findings and instructions for candidate redressal..."
                />
              </div>

              <div className="p-2.5 bg-red-50 border border-red-200 rounded-lg text-red-800 text-[11px]">
                Rejecting will store verifier identity (<span className="font-semibold">{currentUser.full_name}</span>), 
                lock verification status to REJECTED, and append an irreversible audit journey event.
              </div>

              <div className="pt-3 border-t flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowRejectModal(null)}
                  className="px-3.5 py-1.5 border rounded-lg hover:bg-slate-50 text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg shadow-sm"
                >
                  Confirm Rejection & Store Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Profile Mapping: Demands & Services Modal */}
      {activeMappingEditAthlete && (
        <div className="fixed inset-0 bg-navy-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-start border-b pb-3">
              <div>
                <h3 className="font-bold text-lg text-slate-900 flex items-center gap-1.5">
                  <Sparkles className="w-5 h-5 text-amber-500" /> Edit Demands & Services Matrix
                </h3>
                <p className="text-xs text-slate-500">{activeMappingEditAthlete.name} ({activeMappingEditAthlete.kid})</p>
              </div>
              <button onClick={() => setActiveMappingEditAthlete(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Support Demands / Needs (comma separated)
                </label>
                <input
                  type="text"
                  value={demandInput || (activeMappingEditAthlete.support_demands || []).join(', ')}
                  onChange={(e) => setDemandInput(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                  placeholder="Equipment sponsorship, High-altitude training, Nutritionist"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Services Offered (comma separated)
                </label>
                <input
                  type="text"
                  value={serviceOfferedInput || (activeMappingEditAthlete.services_offered || []).join(', ')}
                  onChange={(e) => setServiceOfferedInput(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                  placeholder="Sparring partner, Demonstration athlete, Junior clinic demo"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Services Needed (comma separated)
                </label>
                <input
                  type="text"
                  value={serviceNeededInput || (activeMappingEditAthlete.services_needed || []).join(', ')}
                  onChange={(e) => setServiceNeededInput(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg"
                  placeholder="Physiotherapy, Biomechanical analysis, Sports psychologist"
                />
              </div>

              <div className="pt-3 border-t flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setActiveMappingEditAthlete(null)}
                  className="px-3.5 py-1.5 border rounded-lg hover:bg-slate-50 text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const demands = (demandInput || (activeMappingEditAthlete.support_demands || []).join(', '))
                      .split(',')
                      .map(s => s.trim())
                      .filter(Boolean);
                    const needed = (serviceNeededInput || (activeMappingEditAthlete.services_needed || []).join(', '))
                      .split(',')
                      .map(s => s.trim())
                      .filter(Boolean);
                    const offered = (serviceOfferedInput || (activeMappingEditAthlete.services_offered || []).join(', '))
                      .split(',')
                      .map(s => s.trim())
                      .filter(Boolean);
                    handleSaveProfileMapping(activeMappingEditAthlete.id, demands, needed, offered);
                  }}
                  className="px-4 py-1.5 bg-navy-900 hover:bg-navy-800 text-amber-300 font-semibold rounded-lg shadow-sm"
                >
                  Save Matrix
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Direct Messaging Chat Drawer */}
      {activeChatRecipient && (
        <div className="fixed bottom-4 right-4 z-50 w-96 bg-white rounded-2xl shadow-2xl border border-slate-300 flex flex-col overflow-hidden animate-in slide-in-from-bottom-5">
          {/* Chat Header */}
          <div className="bg-navy-900 text-white p-3.5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-amber-400/20 text-amber-300 flex items-center justify-center font-bold text-xs">
                {activeChatRecipient.name.charAt(0)}
              </div>
              <div>
                <div className="font-bold text-xs text-amber-300 flex items-center gap-1.5">
                  {activeChatRecipient.name}
                  <span className="text-[10px] bg-navy-800 px-1.5 py-0.2 rounded font-normal text-slate-300">
                    {activeChatRecipient.role}
                  </span>
                </div>
                <div className="text-[10px] text-slate-400">Direct Sports Network Channel</div>
              </div>
            </div>
            <button
              onClick={() => setActiveChatRecipient(null)}
              className="text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Chat History */}
          <div className="p-3 bg-slate-50 flex-1 h-64 overflow-y-auto space-y-2.5 text-xs">
            {messages.filter(m => 
              (m.recipient_id === activeChatRecipient.id || m.sender_id === activeChatRecipient.id || 
               (m.athlete_context_id && m.athlete_context_id === activeChatRecipient.athlete_id))
            ).length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center p-4">
                <MessageSquare className="w-8 h-8 mb-1.5 opacity-40 text-navy-800" />
                <p className="font-medium text-slate-600">Direct Channel Active</p>
                <p className="text-[11px]">Direct peer-to-peer message between player, coach and official.</p>
              </div>
            ) : (
              messages
                .filter(m => 
                  (m.recipient_id === activeChatRecipient.id || m.sender_id === activeChatRecipient.id || 
                   (m.athlete_context_id && m.athlete_context_id === activeChatRecipient.athlete_id))
                )
                .map(msg => {
                  const isMe = msg.sender_id === currentUser.username;
                  return (
                    <div key={msg.id} className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}>
                      <div className={`max-w-[85%] rounded-xl p-2.5 text-xs ${
                        isMe 
                          ? 'bg-navy-900 text-amber-100 rounded-br-none shadow-xs' 
                          : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none shadow-xs'
                      }`}>
                        <div className="text-[10px] opacity-75 mb-0.5 font-semibold">
                          {msg.sender_name} ({msg.sender_role})
                        </div>
                        <div>{msg.message_text}</div>
                      </div>
                      <span className="text-[9px] text-slate-400 mt-0.5 px-1">
                        {new Date(msg.sent_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  );
                })
            )}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-2.5 bg-white border-t border-slate-200 flex items-center gap-1.5">
            <input
              type="text"
              placeholder={`Message ${activeChatRecipient.name}...`}
              value={chatInputText}
              onChange={(e) => setChatInputText(e.target.value)}
              className="flex-1 p-2 border border-slate-300 rounded-lg text-xs outline-none focus:border-navy-900"
            />
            <button
              type="submit"
              disabled={!chatInputText.trim()}
              className="bg-navy-900 hover:bg-navy-800 disabled:opacity-50 text-amber-300 p-2 rounded-lg"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>
      )}

      {/* Go Copilot Interactive Search & Entity Navigation Modal */}
      {isCopilotOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white border border-slate-200 w-full max-w-2xl rounded-2xl shadow-2xl flex flex-col overflow-hidden max-h-[85vh]">
            
            {/* Copilot Header */}
            <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-navy-950 p-4 text-white flex items-center justify-between border-b border-slate-700">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-amber-400/20 border border-amber-400/40 flex items-center justify-center text-amber-300">
                  <Compass className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-extrabold text-base tracking-wide text-white">Go Copilot</h3>
                    <span className="bg-amber-400/20 text-amber-300 border border-amber-400/40 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                      Network Intelligence
                    </span>
                  </div>
                  <p className="text-xs text-slate-300">
                    Search athletes, institutions, districts, facilities & schemes
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsCopilotOpen(false)}
                className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-700/60 transition-colors"
                title="Close Go Copilot"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Quick Suggestion Chips */}
            <div className="bg-slate-50 border-b border-slate-200 px-4 py-2.5 flex items-center gap-2 overflow-x-auto text-xs">
              <span className="text-slate-500 font-semibold shrink-0">Try searching:</span>
              <button
                onClick={() => handleCopilotSearch('Aarav Shinde')}
                className="bg-white hover:bg-amber-50 text-slate-700 hover:text-amber-900 border border-slate-200 hover:border-amber-300 px-2.5 py-1 rounded-full shrink-0 transition-colors"
              >
                👤 Player: Aarav Shinde
              </button>
              <button
                onClick={() => handleCopilotSearch('Balewadi High Performance')}
                className="bg-white hover:bg-amber-50 text-slate-700 hover:text-amber-900 border border-slate-200 hover:border-amber-300 px-2.5 py-1 rounded-full shrink-0 transition-colors"
              >
                🏟️ Institute: Balewadi
              </button>
              <button
                onClick={() => handleCopilotSearch('Pune')}
                className="bg-white hover:bg-amber-50 text-slate-700 hover:text-amber-900 border border-slate-200 hover:border-amber-300 px-2.5 py-1 rounded-full shrink-0 transition-colors"
              >
                📍 Location: Pune
              </button>
              <button
                onClick={() => handleCopilotSearch('Khelo India Scholarship')}
                className="bg-white hover:bg-amber-50 text-slate-700 hover:text-amber-900 border border-slate-200 hover:border-amber-300 px-2.5 py-1 rounded-full shrink-0 transition-colors"
              >
                📜 Scheme: KIS
              </button>
            </div>

            {/* Copilot Chat Feed */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
              {copilotChatHistory.map((item) => (
                <div
                  key={item.id}
                  className={`flex flex-col ${item.sender === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-3.5 text-xs ${
                      item.sender === 'user'
                        ? 'bg-navy-900 text-white rounded-br-xs shadow-xs'
                        : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs shadow-xs'
                    }`}
                  >
                    <p className="leading-relaxed font-medium">{item.text}</p>
                    
                    {/* Render Interactive Entity Links */}
                    {item.links && item.links.length > 0 && (
                      <div className="mt-3 space-y-2 pt-2 border-t border-slate-100">
                        <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                          Direct Entity Links:
                        </span>
                        <div className="grid grid-cols-1 gap-2">
                          {item.links.map((link, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleCopilotLinkClick(link)}
                              className="w-full text-left bg-slate-50 hover:bg-amber-50/80 border border-slate-200 hover:border-amber-400 p-2.5 rounded-xl transition-all flex items-center justify-between group shadow-2xs"
                            >
                              <div className="flex items-center gap-2.5">
                                <div className="p-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 group-hover:text-amber-600">
                                  {link.type === 'athlete' && <Users className="w-4 h-4" />}
                                  {link.type === 'facility' && <Building className="w-4 h-4" />}
                                  {link.type === 'scheme' && <Award className="w-4 h-4" />}
                                  {link.type === 'location' && <MapPin className="w-4 h-4" />}
                                </div>
                                <div>
                                  <div className="font-bold text-slate-900 group-hover:text-amber-900 flex items-center gap-1.5">
                                    <span>{link.title}</span>
                                    <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-semibold uppercase">
                                      {link.type}
                                    </span>
                                  </div>
                                  <div className="text-[11px] text-slate-500 font-medium">
                                    {link.subtitle}
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center gap-1 text-slate-400 group-hover:text-amber-600 font-semibold text-[11px]">
                                <span>Open</span>
                                <ExternalLink className="w-3.5 h-3.5" />
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400 mt-1 px-1">{item.timestamp}</span>
                </div>
              ))}
            </div>

            {/* Copilot Search Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleCopilotSearch(copilotSearchQuery);
              }}
              className="p-3 bg-white border-t border-slate-200 flex items-center gap-2"
            >
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search player profiles, location, institutes or schemes..."
                  value={copilotSearchQuery}
                  onChange={(e) => setCopilotSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 outline-none focus:bg-white focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all font-medium"
                />
              </div>
              <button
                type="submit"
                disabled={!copilotSearchQuery.trim()}
                className="bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 disabled:opacity-40 text-slate-950 font-bold px-4 py-2.5 rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-xs"
              >
                <span>Ask</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Mandatory Provenance Bottom Strip */}
        <footer className="bg-white border-t border-slate-200 py-3 text-xs text-slate-500 mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div>
              <span className="font-semibold text-slate-700">Data as of:</span> {new Date().toLocaleDateString()} · 
              <span className="font-semibold text-slate-700 ml-1">Source:</span> Khelo India Registry / State Sports Directorate (Phase 2 Live)
            </div>
            <div className="flex items-center gap-4">
              <span className="text-slate-400">DPDP Act 2023 Compliant</span>
              <span className="text-slate-400">Small-Cell Privacy Active</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
