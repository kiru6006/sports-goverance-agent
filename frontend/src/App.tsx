import { useState, useEffect } from 'react';
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
  X
} from 'lucide-react';

interface UserContext {
  username: string;
  role: string;
  state_id: string | null;
  district_id: string | null;
  full_name: string;
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
  achievements?: Achievement[];
  journey_events?: JourneyEvent[];
}

interface Metric {
  district_id: string;
  state_id: string;
  sport_code: string;
  sport_name: string;
  age_band: string;
  identified_count: number | null;
  verified_count: number | null;
  supported_count: number | null;
  progressed_count: number | null;
  is_suppressed: boolean;
  as_of: string;
}

interface Facility {
  id: string;
  name: string;
  type: string;
  district_id: string;
  latitude: number;
  longitude: number;
  sports: string[];
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'diagnosis' | 'registry' | 'verification' | 'facilities'>('registry');
  const [currentUser, setCurrentUser] = useState<UserContext>({
    username: 'pune_dso',
    role: 'DISTRICT_OFFICER',
    state_id: 'MH',
    district_id: 'MH-PUN',
    full_name: 'Pune District Sports Officer'
  });
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [selectedAthlete, setSelectedAthlete] = useState<Athlete | null>(null);
  
  // Modals
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
      const [resAth, resMet, resFac] = await Promise.all([
        fetch('/api/v1/registry/athletes', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/pipeline/snapshots', { headers: { 'x-user-id': user.username } }),
        fetch('/api/v1/facilities', { headers: { 'x-user-id': user.username } })
      ]);
      if (resAth.ok && resMet.ok) {
        setAthletes(await resAth.json());
        setMetrics(await resMet.json());
        if (resFac.ok) setFacilities(await resFac.json());
      }
    } catch {
      // Offline fallback handling
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
      if (res.ok) {
        setSelectedAthlete(await res.json());
      }
    } catch {
      console.error("Failed to load athlete profile");
    }
  };

  const checkDuplicateAndSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setDuplicateAlert(null);
    setOnboardSuccess(null);

    // Step 1: Duplicate check
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

    // Step 2: Final submit
    try {
      const res = await fetch('/api/v1/registry/athletes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-user-id': currentUser.username },
        body: JSON.stringify(onboardForm)
      });
      if (res.ok) {
        const created = await res.json();
        setOnboardSuccess(`Successfully onboarded athlete with provisional KID: ${created.kid}`);
        setShowOnboardModal(false);
        setDuplicateAlert(null);
        fetchData(currentUser);
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (err) {
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
        if (selectedAthlete && selectedAthlete.id === athleteId) {
          viewAthleteProfile(athleteId);
        }
      } else {
        const err = await res.json();
        alert(`Verification rejected: ${err.detail}`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-100 text-slate-800">
      {/* Top Auditable App Shell */}
      <header className="bg-navy-900 text-white shadow-md border-b border-navy-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ShieldCheck className="w-8 h-8 text-amber-400" />
            <div>
              <h1 className="text-xl font-bold tracking-tight">TrackNet / NSIS</h1>
              <p className="text-xs text-slate-300">Phase 1: Unified Registry & Verification System</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center bg-navy-800 border border-navy-700 rounded-lg p-1 text-xs">
              <span className="text-slate-400 px-2">Role Switcher:</span>
              <select
                className="bg-navy-900 text-amber-300 font-semibold rounded px-2 py-1 outline-none border border-navy-700"
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
            
            <div className="bg-amber-500/20 border border-amber-400/40 text-amber-300 px-2.5 py-1 rounded-md text-xs font-medium flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5" />
              <span>Scope: {currentUser.district_id || currentUser.state_id || 'ALL INDIA'}</span>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-6 text-sm border-t border-navy-800/80">
          <button
            onClick={() => setActiveTab('registry')}
            className={`py-2.5 border-b-2 font-medium flex items-center gap-2 ${
              activeTab === 'registry' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Users className="w-4 h-4" /> Unified Registry
          </button>
          <button
            onClick={() => setActiveTab('verification')}
            className={`py-2.5 border-b-2 font-medium flex items-center gap-2 ${
              activeTab === 'verification' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckCircle className="w-4 h-4" /> Verification Queue
          </button>
          <button
            onClick={() => setActiveTab('diagnosis')}
            className={`py-2.5 border-b-2 font-medium flex items-center gap-2 ${
              activeTab === 'diagnosis' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="w-4 h-4" /> Pipeline Diagnosis
          </button>
          <button
            onClick={() => setActiveTab('facilities')}
            className={`py-2.5 border-b-2 font-medium flex items-center gap-2 ${
              activeTab === 'facilities' ? 'border-amber-400 text-amber-300' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <MapPin className="w-4 h-4" /> Facilities Inventory
          </button>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {onboardSuccess && (
          <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm flex items-center justify-between">
            <span>{onboardSuccess}</span>
            <button onClick={() => setOnboardSuccess(null)} className="text-emerald-600 hover:text-emerald-900"><X className="w-4 h-4" /></button>
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
                          <button
                            onClick={() => viewAthleteProfile(a.id)}
                            className="text-navy-900 hover:text-amber-600 font-medium text-xs flex items-center gap-1 ml-auto"
                          >
                            Profile <ChevronRight className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Verification Queue View */}
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
                            onClick={() => handleVerificationAction(ath.id, 'REJECTED', 'Eligibility criteria unverified')}
                            className="bg-red-50 hover:bg-red-100 text-red-700 px-2.5 py-1.5 rounded text-xs font-medium"
                          >
                            Reject
                          </button>
                          <button
                            onClick={() => handleVerificationAction(ath.id, 'VERIFIED', 'All primary documents verified by DSO')}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1.5 rounded text-xs font-medium"
                          >
                            Verify & Approve
                          </button>
                        </>
                      )}
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

        {/* Pipeline Diagnosis View */}
        {activeTab === 'diagnosis' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Pipeline Retention & Gap Diagnosis</h2>
              <p className="text-xs text-slate-500">Sport × District × Age-Band Funnel with Small-Cell Suppression (&lt;5)</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {metrics.map((m, idx) => (
                <div key={idx} className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
                  <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-4">
                    <div>
                      <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                        {m.sport_name} ({m.sport_code})
                      </span>
                      <h3 className="font-semibold text-slate-800 mt-1">
                        District: {m.district_id} · Band: {m.age_band}
                      </h3>
                    </div>
                    {m.is_suppressed && (
                      <span className="inline-flex items-center gap-1 text-xs text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded">
                        <EyeOff className="w-3.5 h-3.5" /> Privacy Suppressed (&lt;5)
                      </span>
                    )}
                  </div>

                  {m.is_suppressed ? (
                    <div className="p-6 bg-slate-50 rounded-lg text-center text-sm text-slate-500 border border-dashed border-slate-300">
                      Identified count is under threshold (&lt;5). Numbers redacted to prevent individual re-identification.
                    </div>
                  ) : (
                    <div className="grid grid-cols-4 gap-2 text-center">
                      <div className="bg-slate-50 p-2.5 rounded-lg">
                        <div className="text-xs text-slate-500">Identified</div>
                        <div className="text-xl font-bold text-slate-800">{m.identified_count}</div>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-lg">
                        <div className="text-xs text-slate-500">Verified</div>
                        <div className="text-xl font-bold text-blue-600">{m.verified_count}</div>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-lg">
                        <div className="text-xs text-slate-500">Supported</div>
                        <div className="text-xl font-bold text-emerald-600">{m.supported_count}</div>
                      </div>
                      <div className="bg-slate-50 p-2.5 rounded-lg">
                        <div className="text-xs text-slate-500">Progressed</div>
                        <div className="text-xl font-bold text-amber-600">{m.progressed_count}</div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Onboarding Modal with Duplicate-Candidate Warning */}
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

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700">State</label>
                  <input
                    type="text"
                    disabled
                    value={onboardForm.state_id}
                    className="w-full mt-1 p-2 border bg-slate-50 rounded-lg text-slate-500"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700">District</label>
                  <input
                    type="text"
                    disabled
                    value={onboardForm.district_id}
                    className="w-full mt-1 p-2 border bg-slate-50 rounded-lg text-slate-500"
                  />
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

              {/* Minor Consent Block */}
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

      {/* Athlete Profile Modal (Tabs: Achievements & Journey Timeline) */}
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

            {/* Achievements Section */}
            <div className="space-y-2">
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

            {/* Append-Only Journey Timeline */}
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

      {/* Mandatory Provenance Bottom Strip */}
      <footer className="bg-white border-t border-slate-200 py-3 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <span className="font-semibold text-slate-700">Data as of:</span> {new Date().toLocaleDateString()} · 
            <span className="font-semibold text-slate-700 ml-1">Source:</span> Khelo India Registry / State Sports Directorate (Phase 1 Validated)
          </div>
          <div className="flex items-center gap-4">
            <span className="text-slate-400">DPDP Act 2023 Compliant</span>
            <span className="text-slate-400">MeitY Residency Guard</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
