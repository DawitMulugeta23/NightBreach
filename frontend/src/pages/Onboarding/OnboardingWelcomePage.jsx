import { ArrowRight, Shield, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";

function OnboardingWelcomePage() {
  const navigate = useNavigate();
  return (
    <div className="nb-page nb-grid">
      <div className="mx-auto max-w-3xl px-6 py-16 text-center">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-blue-500/20 bg-blue-500/10">
          <Shield className="h-7 w-7 text-blue-400" />
        </div>

        <h1 className="mt-6 text-3xl font-bold text-white sm:text-4xl">
          Welcome to NightBreach
        </h1>

        <p className="mx-auto mt-4 max-w-xl text-sm leading-7 text-slate-400">
          Before we recommend where to start, we'd like to understand your
          goals, current technical background, and practical experience. This
          takes a few minutes and you can change your path at any time.
        </p>

        <div className="mt-8 flex justify-center gap-3">
          <button
            type="button"
            onClick={() => navigate("/onboarding/assessment")}
            className="nb-button-primary inline-flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold"
          >
            <Sparkles className="h-4 w-4" />
            Start Assessment
          </button>

          <button
            type="button"
            onClick={() => navigate("/dashboard")}
            className="nb-button-secondary inline-flex items-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold"
          >
            Skip for now
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default OnboardingWelcomePage;
