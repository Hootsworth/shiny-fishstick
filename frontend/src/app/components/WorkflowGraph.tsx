import React, { useState } from 'react';
import { ChevronRight, Workflow, Plus, Trash2, ArrowUp, ArrowDown, Save, Edit2, X } from 'lucide-react';
import * as api from '../lib/api';

interface Step {
  action: string;
  source_page: string;
  target_page: string;
}

interface WorkflowItem {
  id: string;
  name: string;
  description: string;
  steps: Step[];
}

interface ActionItem {
  id: string;
  name: string;
  action_type: string;
}

interface WorkflowGraphProps {
  workflows: WorkflowItem[];
  actions: ActionItem[];
  onWorkflowsUpdated?: () => void;
}

export function WorkflowGraph({ workflows, actions, onWorkflowsUpdated }: WorkflowGraphProps) {
  const [editingWfId, setEditingWfId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editSteps, setEditSteps] = useState<Step[]>([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  const startEditing = (wf: WorkflowItem) => {
    setEditingWfId(wf.id);
    setEditName(wf.name);
    setEditDescription(wf.description);
    setEditSteps([...wf.steps]);
    setMessage('');
  };

  const cancelEditing = () => {
    setEditingWfId(null);
  };

  const handleStepChange = (index: number, field: keyof Step, value: string) => {
    const updated = [...editSteps];
    updated[index] = { ...updated[index], [field]: value };
    setEditSteps(updated);
  };

  const addStep = () => {
    setEditSteps([...editSteps, { action: actions[0]?.name || 'login', source_page: '/', target_page: '/' }]);
  };

  const removeStep = (index: number) => {
    const updated = editSteps.filter((_, i) => i !== index);
    setEditSteps(updated);
  };

  const moveStep = (index: number, direction: 'up' | 'down') => {
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === editSteps.length - 1) return;

    const targetIdx = direction === 'up' ? index - 1 : index + 1;
    const updated = [...editSteps];
    const temp = updated[index];
    updated[index] = updated[targetIdx];
    updated[targetIdx] = temp;
    setEditSteps(updated);
  };

  const saveWorkflow = async () => {
    if (!editingWfId) return;
    setSaving(true);
    setMessage('');
    try {
      await api.updateWorkflow(editingWfId, editName, editDescription, editSteps);
      setMessage('Workflow saved successfully!');
      setEditingWfId(null);
      if (onWorkflowsUpdated) {
        onWorkflowsUpdated();
      }
    } catch (e: any) {
      setMessage(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="display-title text-2xl flex items-center gap-3 text-[var(--ink)]">
          <Workflow className="h-7 w-7 text-[var(--pie-green-deep)]" />
          <span>FSM Workflow Graph</span>
        </h2>
        <p className="text-[var(--ink-soft)] text-xs font-semibold mt-1">Sequential step logic transition graphs mapped for agents.</p>
      </div>

      {message && (
        <div className="bg-[var(--paper)] border border-[var(--pie-green)] p-4 rounded-xl text-xs font-semibold text-[var(--ink)] shadow-sm">
          {message}
        </div>
      )}

      {workflows.map((wf) => {
        const isEditing = editingWfId === wf.id;

        return (
          <div key={wf.id} className="bg-[var(--paper)] border border-[var(--line)] rounded-[24px] p-8 shadow-sm">
            {isEditing ? (
              // EDIT PANEL
              <div className="space-y-6">
                <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                  <div className="space-y-4 flex-grow max-w-xl w-full">
                    <div>
                      <label className="block text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1">Workflow Name</label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-full px-4 py-2 text-xs font-semibold text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--pie-green)]"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-1">Description</label>
                      <textarea
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        className="w-full bg-[var(--cream)] border border-[var(--line)] rounded-[16px] p-4 text-xs font-semibold text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--pie-green)]"
                        rows={2}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2 w-full md:w-auto">
                    <button
                      onClick={saveWorkflow}
                      disabled={saving}
                      className="w-full md:w-auto bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] border border-[var(--line)] font-bold px-5 py-2.5 rounded-full text-xs uppercase tracking-wider transition shadow-sm flex items-center justify-center gap-2"
                    >
                      <Save className="h-4 w-4" />
                      <span>{saving ? 'Saving...' : 'Save'}</span>
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="w-full md:w-auto bg-[var(--paper)] text-[var(--ink)] border border-[var(--line)] font-bold px-5 py-2.5 rounded-full text-xs uppercase tracking-wider hover:bg-[var(--cream)] transition shadow-sm flex items-center justify-center gap-2"
                    >
                      <X className="h-4 w-4" />
                      <span>Cancel</span>
                    </button>
                  </div>
                </div>

                {/* EDIT STEPS CANVAS */}
                <div className="border-t border-[var(--line)] pt-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="text-[10px] font-bold text-[var(--ink-soft)] uppercase tracking-wider">Workflow Transition Steps</h4>
                    <button
                      onClick={addStep}
                      className="bg-[var(--paper)] text-[var(--ink)] border border-[var(--line)] font-bold px-4 py-2 rounded-full text-[10px] uppercase tracking-wider hover:bg-[var(--cream)] transition shadow-sm flex items-center gap-2"
                    >
                      <Plus className="h-4 w-4 text-[var(--pie-green-deep)]" />
                      Add Step
                    </button>
                  </div>

                  <div className="space-y-3">
                    {editSteps.map((step, idx) => (
                      <div key={idx} className="flex flex-col lg:flex-row items-center gap-3 bg-[var(--cream)] border border-[var(--line)] p-4 rounded-[16px]">
                        <span className="font-bold text-[10px] uppercase px-3 py-1 bg-[var(--paper)] border border-[var(--line)] rounded-full text-[var(--ink)]">Step {idx + 1}</span>
                        
                        <div className="flex-grow grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
                          <div>
                            <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-0.5">Action</label>
                            <select
                              value={step.action}
                              onChange={(e) => handleStepChange(idx, 'action', e.target.value)}
                              className="w-full bg-[var(--paper)] border border-[var(--line)] rounded-full px-3 py-1.5 text-xs font-semibold text-[var(--ink)] focus:outline-none"
                            >
                              {actions.map((act) => (
                                <option key={act.id} value={act.name}>{act.name} ({act.action_type})</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-0.5">Source Route</label>
                            <input
                              type="text"
                              value={step.source_page}
                              onChange={(e) => handleStepChange(idx, 'source_page', e.target.value)}
                              placeholder="/"
                              className="w-full bg-[var(--paper)] border border-[var(--line)] rounded-full px-3 py-1.5 text-xs font-mono text-[var(--ink)] focus:outline-none"
                            />
                          </div>
                          <div>
                            <label className="block text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider mb-0.5">Target Route</label>
                            <input
                              type="text"
                              value={step.target_page}
                              onChange={(e) => handleStepChange(idx, 'target_page', e.target.value)}
                              placeholder="/"
                              className="w-full bg-[var(--paper)] border border-[var(--line)] rounded-full px-3 py-1.5 text-xs font-mono text-[var(--ink)] focus:outline-none"
                            />
                          </div>
                        </div>

                        <div className="flex items-center gap-1 mt-2 lg:mt-0 lg:self-end">
                          <button
                            onClick={() => moveStep(idx, 'up')}
                            disabled={idx === 0}
                            className="p-2 border border-[var(--line)] bg-[var(--paper)] rounded-full text-[var(--ink)] hover:bg-[var(--cream)] disabled:opacity-30"
                          >
                            <ArrowUp className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => moveStep(idx, 'down')}
                            disabled={idx === editSteps.length - 1}
                            className="p-2 border border-[var(--line)] bg-[var(--paper)] rounded-full text-[var(--ink)] hover:bg-[var(--cream)] disabled:opacity-30"
                          >
                            <ArrowDown className="h-3.5 w-3.5" />
                          </button>
                          <button
                            onClick={() => removeStep(idx)}
                            className="p-2 border border-[var(--line)] bg-red-50 hover:bg-red-100 rounded-full text-red-600"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              // READ-ONLY DISPLAY CANVAS
              <div>
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="font-extrabold text-lg uppercase tracking-tight text-[var(--ink)] mb-1">{wf.name}</h3>
                    <p className="text-[var(--ink-soft)] text-xs font-medium leading-relaxed">{wf.description}</p>
                  </div>
                  <button
                    onClick={() => startEditing(wf)}
                    className="bg-[var(--cream)] hover:bg-opacity-85 text-[var(--ink)] border border-[var(--line)] font-bold px-4 py-2 rounded-full text-xs uppercase tracking-wider transition shadow-sm flex items-center gap-2"
                  >
                    <Edit2 className="h-3.5 w-3.5" />
                    <span>Edit Flow</span>
                  </button>
                </div>

                <div className="flex flex-col md:flex-row items-center justify-between gap-4 relative mt-10">
                  {wf.steps.map((step, index) => (
                    <React.Fragment key={index}>
                      <div className="bg-[var(--cream)] border border-[var(--line)] rounded-[24px] p-6 w-full md:w-64 text-center relative z-10 hover:border-[var(--pie-green)] transition duration-200">
                        <div className="text-[9px] font-bold text-[var(--ink-soft)] uppercase tracking-wider bg-[var(--paper)] border border-[var(--line)] rounded-full inline-block px-3 py-1 mb-3">
                          Step {index + 1}
                        </div>
                        <div className="font-extrabold text-sm uppercase mb-4 text-[var(--ink)] tracking-tight">{step.action}</div>
                        <div className="text-[10px] font-bold text-[var(--ink-soft)] flex justify-between border-t border-[var(--line)] pt-3">
                          <span className="bg-[var(--paper)] px-2 py-0.5 rounded-full border border-[var(--line)] font-mono">{step.source_page}</span>
                          <ChevronRight className="h-3.5 w-3.5 text-[var(--ink-soft)] mx-1 self-center" />
                          <span className="bg-[var(--paper)] px-2 py-0.5 rounded-full border border-[var(--line)] font-mono">{step.target_page}</span>
                        </div>
                      </div>
                      {index < wf.steps.length - 1 && (
                        <div className="hidden md:block flex-grow border-t-2 border-dashed border-[var(--line)] relative top-0 mx-2">
                          <span className="absolute -right-1 -top-1.5 h-3 w-3 bg-[var(--paper)] border border-[var(--line)] rounded-full"></span>
                        </div>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
