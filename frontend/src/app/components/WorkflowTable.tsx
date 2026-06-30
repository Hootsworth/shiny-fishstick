import React, { useState } from 'react';
import { Compass, Plus, Trash2, Save, Edit2, X, Play, Loader, ShieldAlert, CheckCircle } from 'lucide-react';
import * as api from '../lib/api';

interface Parameter {
  name: string;
  type: string;
  selector?: string;
}

interface AssertionItem {
  type: 'visible' | 'not_visible' | 'contains_text' | 'url_equals';
  selector?: string;
  value?: string;
}

interface Action {
  id: string;
  name: string;
  description: string;
  action_type: string;
  confidence_score: number;
  selector: string;
  parameters: string;
  assertions?: string;
}

interface WorkflowTableProps {
  projectId: string;
  actions: Action[];
  onActionsUpdated?: () => void;
}

export function WorkflowTable({ projectId, actions, onActionsUpdated }: WorkflowTableProps) {
  const [editingActionId, setEditingActionId] = useState<string | null>(null);
  const [editAssertions, setEditAssertions] = useState<AssertionItem[]>([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // Playground state
  const [testingActionId, setTestingActionId] = useState<string | null>(null);
  const [testParams, setTestParams] = useState<Record<string, string>>({});
  const [runningPlayground, setRunningPlayground] = useState(false);
  const [playgroundResult, setPlaygroundResult] = useState<any | null>(null);

  const startEditing = (act: Action) => {
    setEditingActionId(act.id);
    let parsed: AssertionItem[] = [];
    try {
      parsed = JSON.parse(act.assertions || '[]');
    } catch (e) {
      parsed = [];
    }
    setEditAssertions(parsed);
    setMessage('');
  };

  const cancelEditing = () => {
    setEditingActionId(null);
  };

  const addAssertion = () => {
    setEditAssertions([...editAssertions, { type: 'visible', selector: '', value: '' }]);
  };

  const removeAssertion = (index: number) => {
    setEditAssertions(editAssertions.filter((_, i) => i !== index));
  };

  const handleAssertionChange = (index: number, field: keyof AssertionItem, value: string) => {
    const updated = [...editAssertions];
    updated[index] = { ...updated[index], [field]: value };
    setEditAssertions(updated);
  };

  const saveAssertions = async (actionId: string) => {
    setSaving(true);
    setMessage('');
    try {
      const filtered = editAssertions.map(item => ({
        type: item.type,
        selector: item.selector?.trim() || '',
        value: item.value?.trim() || ''
      }));

      await api.updateAction(actionId, { assertions: JSON.stringify(filtered) });
      setMessage('Assertions updated successfully!');
      setEditingActionId(null);
      if (onActionsUpdated) {
        onActionsUpdated();
      }
    } catch (e: any) {
      setMessage(`Error saving assertions: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  // Playground runners
  const startTesting = (act: Action) => {
    setTestingActionId(act.id);
    setPlaygroundResult(null);
    const initialParams: Record<string, string> = {};
    try {
      const params = JSON.parse(act.parameters || "[]");
      params.forEach((p: any) => {
        if (p.name !== "_frame_selector") {
          if (act.name === 'login') {
            initialParams[p.name] = p.name === 'email' ? 'admin@example.com' : 'password123';
          } else if (act.name === 'search_products') {
            initialParams[p.name] = 'Quantum';
          } else {
            initialParams[p.name] = '';
          }
        }
      });
    } catch (e) {}
    setTestParams(initialParams);
  };

  const handleParamChange = (name: string, val: string) => {
    setTestParams(prev => ({ ...prev, [name]: val }));
  };

  const runPlayground = async (actionId: string) => {
    setRunningPlayground(true);
    setPlaygroundResult(null);
    try {
      const res = await api.executePlayground(projectId, actionId, testParams);
      setPlaygroundResult(res);
    } catch (e: any) {
      setPlaygroundResult({
        success: false,
        error: `Sandbox execution failed: ${e.message}`,
        assertion_results: []
      });
    } finally {
      setRunningPlayground(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="display-title text-2xl flex items-center gap-3 text-[var(--ink)]">
          <Compass className="h-7 w-7 text-[var(--pie-green-deep)]" />
          <span>Action Explorer</span>
        </h2>
        <p className="text-[var(--ink-soft)] text-xs font-semibold mt-1">Classified elements, DOM selectors, and semantic intents.</p>
      </div>

      {message && (
        <div className="bg-[var(--paper)] border border-[var(--pie-green)] p-4 rounded-xl text-xs font-semibold text-[var(--ink)] shadow-sm">
          {message}
        </div>
      )}

      <div className="space-y-6">
        {actions.map((act) => {
          let params: Parameter[] = [];
          try {
            params = JSON.parse(act.parameters || "[]");
          } catch (e) {
            console.error("Failed to parse action parameters", e);
          }

          let currentAssertions: AssertionItem[] = [];
          try {
            currentAssertions = JSON.parse(act.assertions || "[]");
          } catch (e) {
            currentAssertions = [];
          }

          const isEditing = editingActionId === act.id;
          const isTesting = testingActionId === act.id;

          return (
            <div key={act.id} className="bg-[var(--paper)] border border-[var(--line)] rounded-[24px] p-6 shadow-sm">
              <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 border-b border-[var(--line)] pb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="font-extrabold text-sm uppercase tracking-tight text-[var(--ink)]">{act.name}</h3>
                    <span className={`px-3 py-0.5 rounded-full border border-[var(--line)] font-bold text-[10px] uppercase tracking-wider ${act.action_type === 'api' ? 'bg-[var(--pie-green)] text-[var(--ink)]' : 'bg-[var(--cream)] text-[var(--ink-soft)]'}`}>
                      {act.action_type}
                    </span>
                  </div>
                  <p className="text-[var(--ink-soft)] text-xs font-medium mt-1 leading-relaxed">{act.description}</p>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Confidence</span>
                    <strong className="text-xl font-extrabold text-[var(--ink)] tracking-tight">{(act.confidence_score * 100).toFixed(0)}%</strong>
                  </div>
                  {!isEditing && !isTesting && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => startEditing(act)}
                        className="bg-[var(--cream)] hover:bg-opacity-80 text-[var(--ink)] border border-[var(--line)] font-bold px-4 py-2 rounded-full text-xs uppercase tracking-wider transition shadow-sm flex items-center gap-1.5"
                      >
                        <Plus className="h-3.5 w-3.5 text-[var(--pie-green-deep)]" />
                        <span>Assertions</span>
                      </button>
                      <button
                        onClick={() => startTesting(act)}
                        className="bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] border border-[var(--line)] font-bold px-4 py-2 rounded-full text-xs uppercase tracking-wider transition shadow-sm flex items-center gap-1.5"
                      >
                        <Play className="h-3.5 w-3.5 fill-current" />
                        <span>Test Run</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* ACTION EDIT MODE: ASSERTION CONFIGURATION */}
              {isEditing && (
                <div className="mt-6 bg-[var(--cream)] border border-[var(--line)] rounded-[20px] p-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Configure E2E Validation Assertions</h4>
                    <button
                      onClick={addAssertion}
                      className="bg-[var(--paper)] text-[var(--ink)] border border-[var(--line)] font-bold px-3 py-1.5 rounded-full text-[10px] uppercase tracking-wider hover:bg-[var(--cream)] transition shadow-sm flex items-center gap-1.5"
                    >
                      <Plus className="h-3.5 w-3.5 text-[var(--pie-green-deep)]" />
                      Add Assertion
                    </button>
                  </div>

                  {editAssertions.length > 0 ? (
                    <div className="space-y-3">
                      {editAssertions.map((assert, idx) => (
                        <div key={idx} className="flex flex-col md:flex-row items-center gap-3 bg-[var(--paper)] border border-[var(--line)] p-4 rounded-[16px] shadow-inner">
                          <div className="w-full md:w-48">
                            <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1">Check Type</label>
                            <select
                              value={assert.type}
                              onChange={(e) => handleAssertionChange(idx, 'type', e.target.value as any)}
                              className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-full px-3 py-1.5 text-xs text-[var(--ink)] focus:outline-none"
                            >
                              <option value="visible">Is Visible</option>
                              <option value="not_visible">Is Not Visible</option>
                              <option value="contains_text">Contains Text</option>
                              <option value="url_equals">URL Equals</option>
                            </select>
                          </div>
                          
                          <div className="flex-grow w-full">
                            <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1">Target Selector</label>
                            <input
                              type="text"
                              value={assert.selector || ''}
                              onChange={(e) => handleAssertionChange(idx, 'selector', e.target.value)}
                              placeholder="e.g. #welcome-banner"
                              className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-full px-4 py-1.5 text-xs font-mono text-[var(--ink)] focus:outline-none"
                            />
                          </div>

                          <div className="flex-grow w-full">
                            <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1">Expected Value</label>
                            <input
                              type="text"
                              value={assert.value || ''}
                              onChange={(e) => handleAssertionChange(idx, 'value', e.target.value)}
                              placeholder="e.g. Success banner text"
                              className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-full px-4 py-1.5 text-xs text-[var(--ink)] focus:outline-none"
                            />
                          </div>

                          <button
                            onClick={() => removeAssertion(idx)}
                            className="p-2 border border-[var(--line)] bg-red-50 hover:bg-red-100 rounded-full text-red-600 md:self-end mt-2 md:mt-0"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--ink-soft)] italic">No assertions configured. Add one to run visual validation checks.</p>
                  )}

                  <div className="flex justify-end gap-2 border-t border-[var(--line)] pt-3">
                    <button
                      onClick={() => saveAssertions(act.id)}
                      disabled={saving}
                      className="bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] border border-[var(--line)] font-bold px-4 py-2 rounded-full text-[10px] uppercase tracking-wider transition shadow-sm flex items-center gap-1.5"
                    >
                      <Save className="h-3.5 w-3.5" />
                      <span>{saving ? 'Saving...' : 'Save assertions'}</span>
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="bg-[var(--paper)] text-[var(--ink)] border border-[var(--line)] font-bold px-4 py-2 rounded-full text-[10px] uppercase tracking-wider hover:bg-[var(--cream)] transition shadow-sm flex items-center gap-1.5"
                    >
                      <X className="h-3.5 w-3.5" />
                      <span>Cancel</span>
                    </button>
                  </div>
                </div>
              )}

              {/* ACTION TEST RUN PLAYGROUND */}
              {isTesting && (
                <div className="mt-6 bg-[var(--code-bg)] text-[var(--code-text)] border border-[var(--line)] rounded-[20px] p-6 space-y-6">
                  <div className="flex justify-between items-center border-b border-[var(--ink)] border-opacity-10 pb-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-[var(--pie-green)]">Playground Sandbox Run</h4>
                    <button onClick={() => setTestingActionId(null)} className="text-[var(--ink-soft)] hover:text-[var(--code-text)] transition">
                      <X className="h-4.5 w-4.5" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Inputs */}
                    <div className="space-y-4">
                      <h5 className="text-[10px] font-bold uppercase tracking-wider text-[var(--ink-soft)]">Action Arguments Input</h5>
                      {params.filter(p => p.name !== "_frame_selector").length > 0 ? (
                        <div className="space-y-3">
                          {params.filter(p => p.name !== "_frame_selector").map((p) => (
                            <div key={p.name}>
                              <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1">{p.name}</label>
                              <input
                                type="text"
                                value={testParams[p.name] || ''}
                                onChange={(e) => handleParamChange(p.name, e.target.value)}
                                className="w-full bg-[var(--code-bg)] border border-[var(--ink-soft)] border-opacity-20 rounded-full px-4 py-2 text-xs font-semibold text-[var(--code-text)] focus:outline-none focus:border-[var(--pie-green)]"
                              />
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-[var(--ink-soft)] italic">No input parameters required for this action.</p>
                      )}

                      <button
                        onClick={() => runPlayground(act.id)}
                        disabled={runningPlayground}
                        className="w-full bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] border border-[var(--line)] font-bold py-3.5 rounded-full flex items-center justify-center gap-2 uppercase text-xs tracking-wider transition-all duration-150"
                      >
                        {runningPlayground ? (
                          <>
                            <Loader className="h-4 w-4 animate-spin text-[var(--pie-green)]" />
                            <span>Executing Sandbox Pipeline...</span>
                          </>
                        ) : (
                          <>
                            <Play className="h-3.5 w-3.5 fill-current" />
                            <span>Run Sandbox Test</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Results */}
                    <div className="bg-[var(--code-bg)] border border-[var(--ink-soft)] border-opacity-10 rounded-[16px] p-4 flex flex-col justify-center min-h-[250px]">
                      {runningPlayground && (
                        <div className="text-center space-y-3">
                          <Loader className="h-8 w-8 text-[var(--pie-green)] animate-spin mx-auto" />
                          <p className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Spawning browser context...</p>
                        </div>
                      )}

                      {!runningPlayground && !playgroundResult && (
                        <p className="text-xs text-[var(--ink-soft)] italic text-center">Awaiting execution run...</p>
                      )}

                      {!runningPlayground && playgroundResult && (
                        <div className="space-y-4">
                          <div className="flex justify-between items-center border-b border-[var(--ink)] border-opacity-10 pb-2">
                            <span className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Results</span>
                            <div className="flex items-center gap-2">
                              {playgroundResult.success ? (
                                <span className="bg-green-950/30 text-green-400 border border-green-900/40 text-[9px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1">
                                  <CheckCircle className="h-3 w-3" /> SUCCESS
                                </span>
                              ) : (
                                <span className="bg-red-950/30 text-red-400 border border-red-900/40 text-[9px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider flex items-center gap-1">
                                  <ShieldAlert className="h-3 w-3" /> FAILED
                                </span>
                              )}
                              <span className="text-[var(--ink-soft)] text-xs font-mono">{(playgroundResult.execution_time_ms / 1000).toFixed(2)}s</span>
                            </div>
                          </div>

                          {playgroundResult.error && (
                            <div className="bg-red-950/40 border border-red-900/40 p-3 rounded-[12px] text-xs text-red-300 font-mono leading-relaxed">
                              {playgroundResult.error}
                            </div>
                          )}

                          {playgroundResult.assertion_results?.length > 0 && (
                            <div className="space-y-1.5">
                              <span className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Assertions Evaluation</span>
                              {playgroundResult.assertion_results.map((ast: any, idx: number) => (
                                <div key={idx} className={`text-xs p-2.5 rounded-[12px] border flex justify-between ${ast.passed ? 'bg-green-950/20 border-green-950/50 text-green-400' : 'bg-red-950/20 border-red-950/50 text-red-400'}`}>
                                  <div>
                                    <span className="font-bold uppercase mr-1.5">{ast.type}</span>
                                    {ast.selector && <span className="font-mono text-[10px] opacity-60">[{ast.selector}]</span>}
                                  </div>
                                  <span className="font-bold text-[10px]">{ast.passed ? 'PASSED' : 'FAILED'}</span>
                                </div>
                              ))}
                            </div>
                          )}

                          {playgroundResult.screenshot && (
                            <div className="border border-[var(--ink-soft)] border-opacity-10 p-1 bg-[var(--code-bg)] rounded-[12px] mt-2">
                              <span className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1.5">Page Layout Screenshot</span>
                              <img
                                src={`data:image/png;base64,${playgroundResult.screenshot}`}
                                alt="Sandbox Screenshot"
                                className="w-full max-h-64 object-contain border border-[var(--ink-soft)] border-opacity-10 bg-white rounded-[8px]"
                              />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* READ-ONLY DETAILS AREA */}
              {!isEditing && !isTesting && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <div className="text-[10px] font-bold text-[var(--ink-soft)] mb-2 uppercase tracking-wider">Anchor Selector</div>
                    <code className="block bg-[var(--cream)] p-2.5 border border-[var(--line)] rounded-[12px] font-mono text-xs text-[var(--ink)] font-semibold break-all">{act.selector}</code>
                    
                    {currentAssertions.length > 0 && (
                      <div className="mt-4">
                        <div className="text-[10px] font-bold text-[var(--ink-soft)] mb-2 uppercase tracking-wider">Active Assertions</div>
                        <div className="space-y-1">
                          {currentAssertions.map((a, idx) => (
                            <div key={idx} className="text-xs bg-[var(--cream)] border border-[var(--line)] p-2.5 rounded-[12px] font-semibold text-[var(--ink)] flex flex-wrap gap-1 items-center">
                              <span className="text-[var(--pie-green-deep)] uppercase font-bold mr-1">{a.type}</span>
                              {a.selector && <span className="text-[var(--ink-soft)] font-mono">[{a.selector}]</span>}
                              {a.value && <span className="text-[var(--ink)] font-extrabold">→ "{a.value}"</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="text-[10px] font-bold text-[var(--ink-soft)] mb-2 uppercase tracking-wider">Required Arguments</div>
                    {params.length > 0 ? (
                      <div className="space-y-1.5">
                        {params.map((p, idx) => (
                          <div key={idx} className="text-xs font-semibold flex items-center gap-2 bg-[var(--cream)] p-2.5 border border-[var(--line)] rounded-[12px] text-[var(--ink)]">
                            <span className="font-extrabold">{p.name}</span>
                            <span className="text-[var(--ink-soft)] text-[10px] uppercase font-bold">({p.type})</span>
                            {p.selector && <code className="ml-auto text-[10px] bg-[var(--paper)] px-2.5 py-0.5 rounded-full border border-[var(--line)] font-mono text-[var(--ink-soft)]">{p.selector}</code>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="block bg-[var(--cream)] p-2.5 border border-[var(--line)] rounded-[12px] text-xs text-[var(--ink-soft)] italic">No parameters required for this action.</span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
