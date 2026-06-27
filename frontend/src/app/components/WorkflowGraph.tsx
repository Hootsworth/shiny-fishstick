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
        <h2 className="text-3xl font-black tracking-tight flex items-center gap-3">
          <Workflow className="h-8 w-8" />
          STATE MACHINES
        </h2>
        <p className="text-gray-600 font-medium mt-2">Sequential step logic mapped for agents.</p>
      </div>

      {message && (
        <div className="bg-pink-100 border-2 border-black p-4 font-bold text-sm uppercase tracking-wide">
          {message}
        </div>
      )}

      {workflows.map((wf) => {
        const isEditing = editingWfId === wf.id;

        return (
          <div key={wf.id} className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] rounded-md p-8">
            {isEditing ? (
              // EDIT PANEL
              <div className="space-y-6">
                <div className="flex justify-between items-start gap-4">
                  <div className="space-y-4 flex-grow max-w-xl">
                    <div>
                      <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Workflow Name</label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full border-2 border-black p-2 font-bold focus:outline-none focus:ring-0 focus:border-pink-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-1">Description</label>
                      <textarea
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        className="w-full border-2 border-black p-2 font-bold focus:outline-none focus:ring-0 focus:border-pink-500"
                        rows={2}
                      />
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={saveWorkflow}
                      disabled={saving}
                      className="bg-green-400 hover:bg-green-500 border-2 border-black font-black p-3 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <Save className="h-4 w-4" />
                      {saving ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="bg-gray-100 hover:bg-gray-200 border-2 border-black font-black p-3 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <X className="h-4 w-4" />
                      Cancel
                    </button>
                  </div>
                </div>

                {/* EDIT STEPS CANVAS */}
                <div className="border-t-2 border-gray-100 pt-6 space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="text-sm font-black text-gray-500 uppercase tracking-widest">Workflow Transition Steps</h4>
                    <button
                      onClick={addStep}
                      className="bg-pink-200 hover:bg-pink-300 border-2 border-black font-black px-3 py-1.5 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                    >
                      <Plus className="h-4 w-4" />
                      Add Step
                    </button>
                  </div>

                  <div className="space-y-3">
                    {editSteps.map((step, idx) => (
                      <div key={idx} className="flex flex-col md:flex-row items-center gap-3 bg-gray-50 border-2 border-black p-4">
                        <span className="font-black text-sm uppercase px-2 py-1 bg-pink-100 border border-pink-300">Step {idx + 1}</span>
                        
                        <div className="flex-grow grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
                          <div>
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Action</label>
                            <select
                              value={step.action}
                              onChange={(e) => handleStepChange(idx, 'action', e.target.value)}
                              className="w-full bg-white border border-gray-300 p-1.5 font-bold text-sm focus:outline-none focus:border-black"
                            >
                              {actions.map((act) => (
                                <option key={act.id} value={act.name}>{act.name} ({act.action_type})</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Source Page</label>
                            <input
                              type="text"
                              value={step.source_page}
                              onChange={(e) => handleStepChange(idx, 'source_page', e.target.value)}
                              placeholder="/"
                              className="w-full border border-gray-300 p-1.5 font-mono text-sm focus:outline-none focus:border-black"
                            />
                          </div>
                          <div>
                            <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-0.5">Target Page</label>
                            <input
                              type="text"
                              value={step.target_page}
                              onChange={(e) => handleStepChange(idx, 'target_page', e.target.value)}
                              placeholder="/"
                              className="w-full border border-gray-300 p-1.5 font-mono text-sm focus:outline-none focus:border-black"
                            />
                          </div>
                        </div>

                        <div className="flex items-center gap-1.5 md:self-end mt-2 md:mt-0">
                          <button
                            onClick={() => moveStep(idx, 'up')}
                            disabled={idx === 0}
                            className="p-1.5 border border-black bg-white hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-white"
                          >
                            <ArrowUp className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => moveStep(idx, 'down')}
                            disabled={idx === editSteps.length - 1}
                            className="p-1.5 border border-black bg-white hover:bg-gray-100 disabled:opacity-30 disabled:hover:bg-white"
                          >
                            <ArrowDown className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => removeStep(idx)}
                            className="p-1.5 border border-black bg-red-100 hover:bg-red-200 text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
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
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-black uppercase mb-2">{wf.name}</h3>
                    <p className="text-gray-600 font-medium">{wf.description}</p>
                  </div>
                  <button
                    onClick={() => startEditing(wf)}
                    className="bg-yellow-200 hover:bg-yellow-300 border-2 border-black font-black px-4 py-2 flex items-center gap-2 uppercase text-xs tracking-wider shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                  >
                    <Edit2 className="h-4 w-4" />
                    Edit Flow
                  </button>
                </div>

                <div className="flex flex-col md:flex-row items-center justify-between gap-4 relative mt-10">
                  {wf.steps.map((step, index) => (
                    <React.Fragment key={index}>
                      <div className="bg-white border-2 border-black shadow-[4px_4px_0px_0px_#f472b6] p-6 w-full md:w-64 text-center relative z-10">
                        <div className="text-xs font-black text-pink-500 uppercase tracking-widest bg-pink-50 inline-block px-2 py-1 border border-pink-200 mb-3">
                          Step {index + 1}
                        </div>
                        <div className="font-black text-lg uppercase mb-4">{step.action}</div>
                        <div className="text-xs font-bold text-gray-500 flex justify-between border-t-2 border-gray-100 pt-3">
                          <span className="bg-gray-100 px-1">{step.source_page}</span>
                          <ChevronRight className="h-4 w-4 text-black mx-1" />
                          <span className="bg-gray-100 px-1">{step.target_page}</span>
                        </div>
                      </div>
                      {index < wf.steps.length - 1 && (
                        <div className="hidden md:block flex-grow border-t-4 border-dashed border-black relative top-0 mx-2">
                          <span className="absolute -right-2 -top-2.5 h-4 w-4 bg-white border-2 border-black rotate-45"></span>
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
