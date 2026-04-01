'use client';

import { useState, useRef, useEffect, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

const QUESTIONS = [
  { key: 'users',       label: 'Who will use this?' },
  { key: 'core_value',  label: "What\u2019s the one thing it must do better than anything else?" },
  { key: 'scale',       label: 'How many people do you expect to use it in year 1 and year 2?' },
  { key: 'budget',      label: "What\u2019s your monthly cloud hosting budget?" },
  { key: 'timeline',    label: 'When do you need the first version live?' },
  { key: 'compliance',  label: 'Any legal or industry requirements? (e.g. healthcare, payments). If none, say none.' },
];

type Step = 'idea' | 'questions' | 'building' | 'done';

export function IntakeWizard() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('idea');
  const [idea, setIdea] = useState('');
  const [qIndex, setQIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [reviewId, setReviewId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [buildingDots, setBuildingDots] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Animate building dots
  useEffect(() => {
    if (step !== 'building') return;
    const interval = setInterval(() => {
      setBuildingDots((d) => (d.length >= 3 ? '' : d + '.'));
    }, 500);
    return () => clearInterval(interval);
  }, [step]);

  // Auto redirect when done
  useEffect(() => {
    if (step === 'done' && reviewId) {
      const t = setTimeout(() => router.push(`/reviews/${reviewId}`), 1500);
      return () => clearTimeout(t);
    }
  }, [step, reviewId, router]);

  // Focus input when question changes
  useEffect(() => {
    if (step === 'questions') {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [step, qIndex]);

  async function getToken(): Promise<string> {
    if (typeof window !== 'undefined' && (window as any).Clerk?.session) {
      return (await (window as any).Clerk.session.getToken()) ?? '';
    }
    return '';
  }

  async function handleIdeaSubmit(e: FormEvent) {
    e.preventDefault();
    if (!idea.trim()) return;
    setError(null);
    setStep('questions');
  }

  async function handleAnswerSubmit(e: FormEvent) {
    e.preventDefault();
    const answer = currentAnswer.trim() || 'Not specified';
    const key = QUESTIONS[qIndex].key;
    const newAnswers = { ...answers, [key]: answer };
    setAnswers(newAnswers);
    setCurrentAnswer('');

    if (qIndex < QUESTIONS.length - 1) {
      setQIndex(qIndex + 1);
    } else {
      // All answered → submit
      await submitIntake(newAnswers);
    }
  }

  async function submitIntake(finalAnswers: Record<string, string>) {
    setStep('building');
    setError(null);
    try {
      const token = await getToken();
      const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1`;
      const res = await fetch(`${API_BASE}/intake/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ idea, answers: finalAnswers }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Submission failed');
      }
      const data = await res.json();
      setReviewId(data.review_id);
      setStep('done');
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
      setStep('questions');
      setQIndex(QUESTIONS.length - 1);
    }
  }

  const progress = step === 'idea' ? 0 : step === 'questions' ? Math.round((qIndex / QUESTIONS.length) * 100) : 100;

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-white">Idea Mode</h1>
        <p className="mt-2 text-gray-400">
          Describe your product idea in plain English. Get three architecture options from 6 specialist AI architects.
        </p>
      </div>

      {/* Progress bar */}
      {step !== 'building' && step !== 'done' && (
        <div className="mb-8">
          <div className="h-1 w-full rounded-full bg-gray-800">
            <div
              className="h-1 rounded-full bg-archon-500 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-1 text-right text-xs text-gray-600">
            {step === 'idea' ? 'Start' : `Question ${qIndex + 1} of ${QUESTIONS.length}`}
          </p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-900/20 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Step: idea input */}
      {step === 'idea' && (
        <form onSubmit={handleIdeaSubmit} className="space-y-4">
          <label className="block">
            <span className="text-lg font-medium text-white">What do you want to build?</span>
            <textarea
              ref={textareaRef}
              value={idea}
              onChange={(e) => setIdea(e.target.value)}
              placeholder="e.g. A marketplace where freelancers sell digital templates to small businesses..."
              rows={4}
              className="mt-3 w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 text-white placeholder-gray-600 focus:border-archon-500 focus:outline-none focus:ring-1 focus:ring-archon-500"
              autoFocus
            />
          </label>
          <button
            type="submit"
            disabled={!idea.trim()}
            className="w-full rounded-lg bg-archon-500 px-6 py-3 font-medium text-white hover:bg-archon-600 disabled:cursor-not-allowed disabled:opacity-40 transition-colors"
          >
            Get My Architecture &rarr;
          </button>
        </form>
      )}

      {/* Step: one question at a time */}
      {step === 'questions' && (
        <form onSubmit={handleAnswerSubmit} className="space-y-6">
          <div className="rounded-xl border border-gray-800 bg-gray-900/60 p-6">
            <p className="text-xs uppercase tracking-widest text-gray-600 mb-2">
              Question {qIndex + 1} of {QUESTIONS.length}
            </p>
            <p className="text-xl font-medium text-white leading-relaxed">
              {QUESTIONS[qIndex].label}
            </p>
          </div>
          <input
            ref={inputRef}
            type="text"
            value={currentAnswer}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            placeholder="Type your answer here..."
            className="w-full rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 text-white placeholder-gray-600 focus:border-archon-500 focus:outline-none focus:ring-1 focus:ring-archon-500"
          />
          <div className="flex items-center gap-3">
            <button
              type="submit"
              className="flex-1 rounded-lg bg-archon-500 px-6 py-3 font-medium text-white hover:bg-archon-600 transition-colors"
            >
              {qIndex < QUESTIONS.length - 1 ? 'Next \u2192' : 'Build My Architecture \u26A1'}
            </button>
            {qIndex > 0 && (
              <button
                type="button"
                onClick={() => { setQIndex(qIndex - 1); setCurrentAnswer(answers[QUESTIONS[qIndex - 1].key] || ''); }}
                className="rounded-lg border border-gray-700 px-4 py-3 text-sm text-gray-400 hover:border-gray-500 hover:text-white transition-colors"
              >
                &larr; Back
              </button>
            )}
          </div>
          {/* Answered so far */}
          {Object.keys(answers).length > 0 && (
            <div className="space-y-2 pt-2 border-t border-gray-800">
              <p className="text-xs uppercase tracking-widest text-gray-600">Answers so far</p>
              {QUESTIONS.slice(0, qIndex).map((q) => (
                <div key={q.key} className="flex gap-2 text-sm">
                  <span className="text-gray-500 min-w-0 flex-shrink-0">{q.label.split('?')[0]}:</span>
                  <span className="text-gray-300 truncate">{answers[q.key]}</span>
                </div>
              ))}
            </div>
          )}
        </form>
      )}

      {/* Step: building */}
      {step === 'building' && (
        <div className="py-16 text-center space-y-8">
          <div className="space-y-2">
            <p className="text-2xl font-bold text-white">Architects are working{buildingDots}</p>
            <p className="text-gray-400">6 specialists running in parallel. This takes 3\u20135 minutes.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-left">
            {['Software Architect', 'Cloud Architect', 'Security Architect', 'Data Architect', 'Integration Architect', 'AI Architect'].map((name) => (
              <div key={name} className="rounded-lg border border-yellow-800 bg-yellow-900/10 p-3">
                <p className="text-xs font-medium text-yellow-400 animate-pulse">\u26A1 {name}</p>
              </div>
            ))}
          </div>
          <p className="text-sm text-gray-600">You can close this tab. We\u2019ll email you when it\u2019s ready.</p>
        </div>
      )}

      {/* Step: done */}
      {step === 'done' && (
        <div className="py-16 text-center space-y-4">
          <p className="text-4xl">\u2705</p>
          <p className="text-2xl font-bold text-white">Architecture ready!</p>
          <p className="text-gray-400">Redirecting to your results{buildingDots}</p>
        </div>
      )}
    </div>
  );
}
