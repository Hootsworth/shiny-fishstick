import React, { useState } from 'react';
import { Compass, Plus, Trash2, Save, Edit2, X } from 'lucide-react';
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
  actions: Action[];
  onActionsUpdated?: () => void;
}

export function WorkflowTable({ actions, onActionsUpdated }: WorkflowTableProps) {
  const [editingActionId, setEditingActionId] = useState<string | null>(null);
  const [editAssertions, setEditAssertions] = useState<AssertionItem[]>([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

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
      // Filter empty selectors/values if needed, then update
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

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <Compass className="h-8 w-8" />
          ACTION DICTIONARY
        </h2>
        <p className="text-gray-600 font-medium mt-2">Classified DOM elements and agent intents.</p>
      </div>

      {message && (
        <div className="bg-pink-100 border-2 border-black p-4 font-bold text-sm uppercase tracking-wide">
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

          return (
            <div key={act.id} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-6">
              <div className="flex flex-col md:flex-row justify-between md:items-center gap-4 border-b-2 border-gray-100 pb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h3 className="text-xl font-black uppercase">{act.name}</h3>
                    <span className={`px-3 py-1 border-2 border-black font-bold text-xs uppercase tracking-wider ${act.action_type === 'api' ? 'bg-pink-200' : 'bg-gray-100'}`}>
                      {act.action_type}
                    </span>
                  </div>
                  <p className="text-gray-600 font-medium mt-2">{act.description}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="block text-xs font-bold text-gray-500 uppercase tracking-widest">Confidence</span>
                    <strong className="text-2xl font-black">{(act.confidence_score * 100).toFixed(0)}%</strong>
                  </div>
                  {!isEditing && (
                    <button
                      onClick={() => startEditing(act)}
                      className="bg-yellow-200 hover:bg-yellow-300 border-2 border-black font-black px-3 py-1.5 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <Edit2 className="h-4 w-4" />
                      Assertions
                    </button>
                  )}
                </div>
              </div>

              {isEditing ? (
                // EDIT ASSERTIONS PANEL
                <div className="mt-6 bg-gray-50 border-2 border-black p-4 space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="text-sm font-black uppercase tracking-widest text-pink-500">Edit E2E Test Assertions</h4>
                    <button
                      onClick={addAssertion}
                      className="bg-pink-200 hover:bg-pink-300 border-2 border-black font-black px-3 py-1 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <Plus className="h-4 w-4" />
                      Add Assertion
                    </button>
                  </div>

                  {editAssertions.length > 0 ? (
                    <div className="space-y-3">
                      {editAssertions.map((assert, idx) => (
                        <div key={idx} className="flex flex-col md:flex-row items-center gap-3 bg-white border border-gray-300 p-3">
                          <div className="w-full md:w-48">
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Type</label>
                            <select
                              value={assert.type}
                              onChange={(e) => handleAssertionChange(idx, 'type', e.target.value as any)}
                              className="w-full border border-gray-300 p-1 font-bold text-sm focus:outline-none focus:border-black"
                            >
                              <option value="visible">Is Visible</option>
                              <option value="not_visible">Is Not Visible</option>
                              <option value="contains_text">Contains Text</option>
                              <option value="url_equals">URL Equals</option>
                            </select>
                          </div>
                          
                          <div className="flex-grow w-full">
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Selector</label>
                            <input
                              type="text"
                              value={assert.selector || ''}
                              onChange={(e) => handleAssertionChange(idx, 'selector', e.target.value)}
                              placeholder="e.g. #welcome-banner"
                              className="w-full border border-gray-300 p-1 font-mono text-sm focus:outline-none focus:border-black"
                            />
                          </div>

                          <div className="flex-grow w-full">
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Value (Expected)</label>
                            <input
                              type="text"
                              value={assert.value || ''}
                              onChange={(e) => handleAssertionChange(idx, 'value', e.target.value)}
                              placeholder="e.g. admin"
                              className="w-full border border-gray-300 p-1 text-sm focus:outline-none focus:border-black"
                            />
                          </div>

                          <button
                            onClick={() => removeAssertion(idx)}
                            className="p-2 border border-black bg-red-50 hover:bg-red-100 text-red-700 md:self-end"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm font-medium text-gray-500 italic">No assertions set for this action.</p>
                  )}

                  <div className="flex justify-end gap-2 border-t border-gray-200 pt-3">
                    <button
                      onClick={() => saveAssertions(act.id)}
                      disabled={saving}
                      className="bg-green-400 hover:bg-green-500 border-2 border-black font-black px-4 py-1.5 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <Save className="h-4 w-4" />
                      {saving ? 'Saving...' : 'Save Assertions'}
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="bg-white hover:bg-gray-100 border-2 border-black font-black px-4 py-1.5 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <X className="h-4 w-4" />
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                // VIEW MODE DETAILS
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <div className="text-xs font-black text-gray-500 mb-2 uppercase tracking-widest">Anchor Selector</div>
                    <code className="block bg-gray-50 p-2 border-2 border-black rounded-none font-mono text-sm font-bold">{act.selector}</code>
                    
                    {/* DISPLAY ACTIVE ASSERTIONS */}
                    {currentAssertions.length > 0 && (
                      <div className="mt-4">
                        <div className="text-xs font-black text-gray-500 mb-2 uppercase tracking-widest text-pink-500">Active Test Assertions</div>
                        <div className="space-y-1">
                          {currentAssertions.map((a, idx) => (
                            <div key={idx} className="text-xs bg-pink-50 border border-pink-200 p-2 font-medium">
                              <span className="font-bold text-pink-700 uppercase mr-1">{a.type}</span>
                              {a.selector && <span className="text-gray-600 font-mono">[{a.selector}]</span>}
                              {a.value && <span className="text-black font-semibold ml-1">→ "{a.value}"</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="text-xs font-black text-gray-500 mb-2 uppercase tracking-widest">Required Params</div>
                    {params.length > 0 ? (
                      <div className="space-y-2">
                        {params.map((p, idx) => (
                          <div key={idx} className="text-sm font-medium flex items-center gap-2 bg-gray-50 p-2 border-2 border-black">
                            <strong className="text-black">{p.name}</strong>
                            <span className="text-gray-500 text-xs uppercase">({p.type})</span>
                            {p.selector && <code className="ml-auto text-xs bg-white px-2 py-1 border border-black font-mono">{p.selector}</code>}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <span className="block bg-gray-50 p-2 border-2 border-black font-medium text-sm text-gray-500 italic">No parameters required</span>
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
